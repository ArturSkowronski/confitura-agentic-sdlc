"""Klasyfikacja ryzyka zmiany (stacja 4).

Ryzyko liczymy z sygnałów deterministycznych: ścieżek, rozmiaru diffu, testów,
historii modułu, numeru próby. Model nie ma tu głosu, więc prompt injection w diffie
nic nie zmieni. Od poziomu i od pokrycia scenariuszami zależy autonomia (policy.json):

  low / medium    lights-out, jeśli zlecenie ma własne scenariusze holdout; inaczej człowiek
  high / critical człowiek (environment critical-path)

Dwa sygnały są specyficzne dla fabryki:
  - numer próby: każda poprawka przesuwa agenta od wymagania w stronę bramki,
  - brak scenariuszy: bez wyroczni nie ma czego mierzyć, więc nie ma autonomii.

Użycie:
  python3 sdlc/risk.py --base origin/main --head HEAD [--agent] [--attempt 2] [--work-order "tytuł"]
"""

from __future__ import annotations

import argparse

from context import build_index
from lib import STATE, covered_by_scenarios, git, outputs, module_for_path, policy, summary_md, write_json

ORDER = ["low", "medium", "high", "critical"]


def level_for(score: int, levels: dict) -> str:
    return max((name for name in ORDER if score >= levels[name]), key=ORDER.index)


def classify(base: str, head: str, agent_authored: bool, attempt: int = 1, work_order: str = "") -> dict:
    rules = policy()
    index = build_index()
    catalog = index["modules"]
    numstat = [line.split("\t") for line in git("diff", "--numstat", f"{base}...{head}").splitlines() if line]
    files = [{"path": p, "added": int(a) if a.isdigit() else 0, "deleted": int(d) if d.isdigit() else 0} for a, d, p in numstat]
    paths = [f["path"] for f in files]
    lines = sum(f["added"] + f["deleted"] for f in files)
    touched = sorted({m["name"] for p in paths if (m := module_for_path(p, catalog))})
    by_name = {m["name"]: m for m in catalog}

    signals = []

    def signal(name: str, points: int, detail: str) -> None:
        signals.append({"name": name, "points": points, "detail": detail})

    gate_hits = [p for p in paths if any(p.startswith(g) for g in rules["gate_paths"])]
    if gate_hits:
        signal("zmiana bramek", 7, f"zmiana dotyka mechanizmów kontroli: {', '.join(gate_hits[:3])}")

    critical_hits = [p for p in paths if any(p.startswith(c) for c in rules["critical_paths"])]
    critical_hits += [p for p in paths if (m := module_for_path(p, catalog)) and m.get("critical") and p not in critical_hits]
    if critical_hits:
        signal("ścieżka krytyczna", 4, f"{len(critical_hits)} plik(ów) na ścieżce krytycznej")

    sensitive_hits = [p for p in paths if any(p.startswith(s) for s in rules["sensitive_paths"])]
    if sensitive_hits:
        signal("moduł wrażliwy", 2, f"zmiana w bibliotece współdzielonej: {len(sensitive_hits)} plik(ów)")

    radius_critical = sorted({d for name in touched for d in by_name[name]["dependents"] if by_name[d].get("critical")} - set(touched))
    if radius_critical:
        signal("blast radius", 1, f"zmiana może dotrzeć do ścieżki krytycznej: {', '.join(radius_critical)}")

    thresholds = rules["risk"]
    if lines > thresholds["large_diff_lines"]:
        signal("duży diff", 2, f"{lines} zmienionych linii")
    elif lines > thresholds["medium_diff_lines"]:
        signal("średni diff", 1, f"{lines} zmienionych linii")

    main_code = [p for p in paths if "/src/main/" in p]
    test_code = [p for p in paths if "/src/test/" in p]
    if main_code and not test_code:
        signal("brak testów", 2, "zmieniony kod produkcyjny bez żadnej zmiany w testach")

    incidents = sorted({i["title"] for name in touched for i in by_name[name]["incidents"]})
    if incidents:
        signal("historia incydentów", 1, "; ".join(incidents))

    unstable = [name for name in touched if by_name[name]["churn_30d"] >= thresholds["unstable_churn_30d"]]
    if unstable:
        signal("niestabilny moduł", 1, f"dużo zmian w 30 dniach: {', '.join(unstable)}")

    if agent_authored:
        signal("autor: agent", 1, "zmiana wygenerowana przez agenta")

    if attempt > 1:
        signal("poprawka", attempt - 1, f"próba nr {attempt}: agent iteruje pod bramki, nie pod wymaganie")

    covered = covered_by_scenarios(work_order) if work_order else False
    if work_order and not covered:
        signal("brak scenariuszy", 2, "zlecenie nie ma własnych scenariuszy holdout")

    score = sum(s["points"] for s in signals)
    level = level_for(score, thresholds["levels"])
    mode = rules["autonomy"][level]
    if mode == "lights-out" and not covered:
        autonomy, why = "człowiek", "brak scenariuszy holdout: nie ma czym zmierzyć zmiany bez człowieka"
    elif mode == "lights-out":
        autonomy, why = "lights-out", f"ryzyko {level} i zlecenie pokryte scenariuszami"
    else:
        autonomy, why = "człowiek", f"polityka: ryzyko {level} wymaga człowieka"
    owners = []
    for name in touched:
        for owner in by_name[name]["owners_real"][:1]:
            owners.append({"module": name, "name": owner["name"]})
    return {
        "level": level,
        "score": score,
        "signals": signals,
        "modules": touched,
        "files": files,
        "lines": lines,
        "needs_human": autonomy == "człowiek",
        "autonomy": autonomy,
        "autonomy_reason": why,
        "attempt": attempt,
        "covered": covered,
        "suggested_reviewers": owners,
    }


def markdown(result: dict) -> str:
    icon = {"low": "🟢", "medium": "🟡", "high": "🟠", "critical": "🔴"}[result["level"]]
    out = [f"### {icon} Ryzyko: **{result['level']}** ({result['score']} pkt)", ""]
    if result["signals"]:
        out += ["| sygnał | pkt | szczegóły |", "|---|---|---|"]
        out += [f"| {s['name']} | +{s['points']} | {s['detail']} |" for s in result["signals"]]
    else:
        out.append("Brak sygnałów ryzyka.")
    if result["needs_human"]:
        out += ["", f"👤 Autonomia: **człowiek** ({result['autonomy_reason']}). Przebieg czeka w environment `critical-path`."]
    else:
        out += ["", f"🌑 Autonomia: **lights-out** ({result['autonomy_reason']})."]
    return "\n".join(out)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--base", required=True)
    parser.add_argument("--head", default="HEAD")
    parser.add_argument("--agent", action="store_true", help="zmiana wygenerowana przez agenta")
    parser.add_argument("--attempt", type=int, default=1)
    parser.add_argument("--work-order", default="")
    parser.add_argument("--out", default=str(STATE / "risk.json"))
    args = parser.parse_args()

    result = classify(args.base, args.head, args.agent, args.attempt, args.work_order)
    write_json(__import__("pathlib").Path(args.out), result)
    text = markdown(result)
    print(text)
    summary_md(text)
    outputs(level=result["level"], score=result["score"], needs_human=str(result["needs_human"]).lower(),
              autonomy=result["autonomy"])


if __name__ == "__main__":
    main()
