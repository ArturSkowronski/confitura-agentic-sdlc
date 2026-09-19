"""Wyrocznia fabryki (stacja 3): scenariusze holdout, których agent nie widzi.

Dwa poziomy, bo holdout zużywa się z każdym użyciem:

  robocze  gdy nie przechodzą, agent dostaje w pętli poprawek NAZWĘ scenariusza (opis zachowania)
  sejf     tylko decyzja: przyjąć albo odrzucić. Zero informacji zwrotnej. Porażka zapala andon,
           bo każda poprawka „pod sejf” zamieniałaby go w zbiór treningowy.

Sejf uruchamiamy dopiero wtedy, gdy przejdą robocze. Inaczej jego wynik przeciekłby razem
z raportem z pierwszej próby.

Użycie:
  python3 sdlc/scenarios.py run --work-order "Zwroty częściowe"
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import xml.etree.ElementTree as ET

from lib import SCENARIOS, STATE, outputs, scenarios_for, summary_md, write_json


def _maven(ids: list[str]) -> None:
    for module in ids:
        for report in (SCENARIOS / module / "target" / "surefire-reports").glob("*.xml"):
            report.unlink()
    subprocess.run(["mvn", "-B", "-q", "-fae", "-pl", ",".join(ids), "verify", "-Dmaven.test.failure.ignore=true"],
                   cwd=SCENARIOS, capture_output=True, text=True)


def _results(scenario: dict) -> list[dict]:
    reports = list((SCENARIOS / scenario["id"] / "target" / "surefire-reports").glob("TEST-*.xml"))
    if not reports:
        # Nie skompilowało się: zwykle kod nie ma API, które obiecuje specyfikacja zlecenia.
        return [{"set": scenario["id"], "name": f"{scenario['title']}: scenariusze się nie kompilują "
                 "(brak API ze specyfikacji zlecenia?)", "passed": False}]
    out = []
    for report in reports:
        for case in ET.parse(report).getroot().iter("testcase"):
            failed = case.find("failure") is not None or case.find("error") is not None
            out.append({"set": scenario["id"], "name": case.get("name"), "passed": not failed})
    return out


def run(work_order: str) -> dict:
    chosen = scenarios_for(work_order)
    working = [s for s in chosen if not s.get("vault")]
    vault = [s for s in chosen if s.get("vault")]

    _maven([s["id"] for s in working])
    results = [r for s in working for r in _results(s)]
    working_ok = all(r["passed"] for r in results)

    vault_state = "brak"
    if vault and working_ok:
        _maven([s["id"] for s in vault])
        vault_results = [r for s in vault for r in _results(s)]
        vault_state = "przeszedł" if all(r["passed"] for r in vault_results) else "nie przeszedł"
    elif vault:
        vault_state = "nieotwarty"  # robocze nie przeszły, sejfu nie ruszamy

    summary = {
        "work_order": work_order,
        "covered": any(not s.get("always") for s in working),
        "working": results,
        "working_failed": sum(not r["passed"] for r in results),
        "vault": vault_state,
        # to jedyne, co wolno pokazać agentowi przy poprawce
        "feedback": [r["name"] for r in results if not r["passed"]],
    }
    write_json(STATE / "scenarios.json", summary)
    return summary


def markdown(summary: dict) -> str:
    total = len(summary["working"])
    ok = summary["working_failed"] == 0 and summary["vault"] in ("brak", "przeszedł")
    lines = [f"### 🎯 Wyrocznia: {'✅' if ok else '❌'} scenariusze robocze {total - summary['working_failed']}/{total}"
             f" · sejf: {summary['vault']}", ""]
    if not summary["covered"]:
        lines += ["⚠️ Zlecenie nie ma własnych scenariuszy, sprawdziliśmy tylko regresję. Bez nich fabryka nie gasi światła.", ""]
    lines += [f"- {'✅' if r['passed'] else '❌'} {r['name']} <sub>({r['set']})</sub>" for r in summary["working"]]
    if summary["vault"] == "nie przeszedł":
        lines += ["", "🚨 **Sejf nie przeszedł.** Nie mówimy agentowi, który scenariusz ani dlaczego. Andon: potrzebny człowiek."]
    lines += ["", "<sub>Scenariusze pisze człowiek, agent ich nie widzi. Przy poprawce dostaje tylko nazwy nieudanych "
              "scenariuszy roboczych. Sejf nie daje żadnej informacji zwrotnej.</sub>"]
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--work-order", required=True)
    args = parser.parse_args()

    summary = run(args.work_order)
    text = markdown(summary)
    print(text)
    summary_md(text)
    vault_failed = summary["vault"] == "nie przeszedł"
    outputs(covered=str(summary["covered"]).lower(), working_failed=summary["working_failed"],
              vault_failed=str(vault_failed).lower())
    sys.exit(0 if summary["working_failed"] == 0 and not vault_failed else 1)


if __name__ == "__main__":
    main()
