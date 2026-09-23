"""Linia produkcyjna (stacje 4-5): konfiguracja linii, raport poprawki, karta zlecenia.

  line-config   hash wszystkiego, co decyduje o zachowaniu linii (polityka, reguły, kontekst,
                wyrocznia, agent, model). Pracownik jest niedeterministyczny, linia nie może być:
                spadek first-pass yield przypisujesz do konkretnej zmiany konfiguracji.
  feedback      raport dla agenta w pętli poprawek. Z wyroczni tylko NAZWY nieudanych scenariuszy
                roboczych. Sejf nie daje żadnej informacji.
  card          karta zlecenia w PR: próba, decyzja, czas czekania na człowieka, koszt, konfiguracja.
                Ukryty JSON w komentarzu czyta hala (tower/index.html).

Użycie:
  python3 sdlc/factory.py line-config
  python3 sdlc/factory.py feedback
  python3 sdlc/factory.py card --attempt 1 --decision lights-out [--lead-min 7] [--human-wait-min 3]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
from pathlib import Path

import slad
from lib import ROOT, STATE, outputs, load_json, summary_md, write_json

LINE_FILES = ["sdlc/policy.json", "sdlc/review-rules.json", "AGENTS.md", "scenarios/index.json",
              "system/architecture/src/test/java/pl/confitura/shop/architecture/ArchitectureRulesTest.java"]


def line_config() -> dict:
    parts = {}
    for name in LINE_FILES:
        path = ROOT / name
        parts[name] = hashlib.sha256(path.read_bytes()).hexdigest()[:10] if path.exists() else "brak"
    parts["agent"] = os.environ.get("AGENT", "kagent")
    parts["model"] = os.environ.get("LLM_MODEL", "-")
    parts["review_model"] = os.environ.get("LLM_REVIEW_MODEL", os.environ.get("LLM_MODEL", "-"))
    digest = hashlib.sha256(json.dumps(parts, sort_keys=True).encode()).hexdigest()[:12]
    return {"hash": digest, "parts": parts}


def _read(name: str) -> str:
    """Raporty z bramek: najpierw w .sdlc, potem w katalogu wyników przebiegu ($OUT)."""
    for folder in (STATE, Path(os.environ.get("OUT", ""))):
        path = folder / name
        if str(folder) and path.exists():
            return path.read_text(encoding="utf-8")
    return ""


def feedback() -> str:
    """Co dostaje agent przy poprawce. Celowo wąsko: każdy bit informacji o wyroczni to przeciek."""
    sections = []
    build = _read("kontrola-1-build.md")
    if "❌" in build:
        rules = re.findall(r"\*\*Naruszona reguła architektury\*\* \(\d+×\): (.+)", build)
        sections.append("Bramka architektury:\n" + "\n".join(f"- {r}" for r in rules or ["build albo testy są czerwone"]))
    weak = _read("kontrola-2-oslabianie.md")
    if "❌" in weak:
        sections.append("Detektor osłabiania testów zablokował zmianę:\n" + "\n".join(l for l in weak.splitlines() if l.startswith("- ")))
    mutation = _read("kontrola-4-mutacje.md")
    if "❌" in mutation:
        survivors = [l for l in mutation.splitlines() if l.startswith("| `")]
        sections.append("Testy mutacyjne poniżej progu. Przeżyły mutanty:\n" + "\n".join(survivors[:6]))
    scen = STATE / "scenarios.json"
    if scen.exists():
        names = load_json(scen).get("feedback", [])
        if names:
            sections.append("Nie spełnia wymagań (scenariusze akceptacyjne, których nie widzisz):\n"
                            + "\n".join(f"- {n}" for n in names))
    review = _read("review.md")
    blocking = re.search(r"### 🚫 Blokujące\n\n(.*?)(\n### |\n<sub>)", review, re.S)
    if blocking:
        items = [l for l in blocking.group(1).splitlines() if l.startswith("- ")]
        sections.append("Review, znaleziska blokujące:\n" + "\n".join(items))
    return "\n\n".join(sections) or "Kontrola jakości nie przeszła, ale bez szczegółów (np. sejf albo infrastruktura)."


def agent_cost() -> dict:
    """Szacunek kosztu z logu zdarzeń agenta. Format różni się między agentami, więc szukamy ogólnie."""
    cost, tokens_in, tokens_out, final_cost = 0.0, 0, 0, None

    def walk(node):
        nonlocal cost, tokens_in, tokens_out, final_cost
        if isinstance(node, dict):
            for key, value in node.items():
                if key in ("total_cost_usd",) and isinstance(value, (int, float)):
                    final_cost = max(final_cost or 0, float(value))
                elif key == "cost" and isinstance(value, (int, float)):
                    cost += float(value)
                elif key in ("input_tokens", "input") and isinstance(value, int):
                    tokens_in += value
                elif key in ("output_tokens", "output") and isinstance(value, int):
                    tokens_out += value
                else:
                    walk(value)
        elif isinstance(node, list):
            for item in node:
                walk(item)

    events = STATE / "agent-events.jsonl"
    if events.exists():
        for line in events.read_text(encoding="utf-8").splitlines():
            try:
                walk(json.loads(line))
            except json.JSONDecodeError:
                continue
    return {"usd": round(final_cost if final_cost is not None else cost, 4), "tokens_in": tokens_in, "tokens_out": tokens_out}


DECISIONS = {
    "lights-out": "🌑 przyjęte bez człowieka (lights-out)",
    "człowiek": "👤 przyjęte przez człowieka",
    "czeka": "👤 czeka na człowieka",
    "poprawka": "🔁 odesłane do poprawki",
    "andon": "🚨 andon: linia zatrzymana, potrzebny człowiek",
    "odrzucone": "↩️ odesłane przy przyjęciu",
}


def card(attempt: int, decision: str, lead_min: float | None, human_wait_min: float | None) -> str:
    config = line_config()
    cost = agent_cost()
    trace = slad.url(slad.Step().trace_id)
    risk = load_json(STATE / "risk.json") if (STATE / "risk.json").exists() else {}
    data = {
        "attempt": attempt,
        "decision": decision,
        "first_pass": attempt == 1 and decision in ("lights-out", "człowiek"),
        "risk": risk.get("level"),
        "lead_min": lead_min,
        "human_wait_min": human_wait_min,
        "cost_usd": cost["usd"],
        "tokens": cost["tokens_in"] + cost["tokens_out"],
        "config": config["hash"],
        "trace": trace,
    }
    write_json(STATE / "card.json", data)
    fmt = lambda v, unit: "-" if v is None else f"{v:.0f} {unit}"
    lines = [
        "### 🏭 Karta zlecenia",
        "",
        "| | |",
        "|---|---|",
        f"| Decyzja | {DECISIONS.get(decision, decision)} |",
        f"| Próba | {attempt}{' (first pass)' if data['first_pass'] else ''} |",
        f"| Ryzyko | {risk.get('level', '-')} |",
        f"| Lead time (od etykiety `agent`) | {fmt(lead_min, 'min')} |",
        f"| Czekanie na człowieka | {fmt(human_wait_min, 'min')} |",
        f"| Koszt agenta (szacunek) | {cost['usd']:.2f} USD, {data['tokens']:,} tokenów |".replace(",", " "),
        f"| Konfiguracja linii | `{config['hash']}` |",
        *([f"| Ślad | [Jaeger]({trace}) |"] if trace else []),
        "",
        f"<!-- factory-card {json.dumps(data, ensure_ascii=False)} -->",
    ]
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("line-config")
    sub.add_parser("feedback")
    c = sub.add_parser("card")
    c.add_argument("--attempt", type=int, default=1)
    c.add_argument("--decision", required=True)
    c.add_argument("--lead-min", type=float)
    c.add_argument("--human-wait-min", type=float)
    args = parser.parse_args()

    if args.cmd == "line-config":
        config = line_config()
        write_json(STATE / "line-config.json", config)
        print(json.dumps(config, ensure_ascii=False))
        outputs(hash=config["hash"])
    elif args.cmd == "feedback":
        text = feedback()
        (STATE / "feedback.md").write_text(text, encoding="utf-8")
        print(text)
    else:
        text = card(args.attempt, args.decision, args.lead_min, args.human_wait_min)
        (STATE / "card.md").write_text(text, encoding="utf-8")
        print(text)
        summary_md(text)


if __name__ == "__main__":
    main()
