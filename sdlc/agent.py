"""Sterownik wykonawcy. Agent jest wymienny, platforma zostaje.

  AGENT=kagent   (domyślnie) agent `wykonawca` w kagent, przez A2A; pracuje na /work/repo narzędziami MCP
  AGENT=replay   bez sieci i bez modelu: nakłada nagraną łatkę pasującą do zlecenia, routingu i próby

ATTEMPT=2 z plikiem .sdlc/feedback.md to pętla poprawek: agent dostaje raport z kontroli jakości
(bez treści scenariuszy holdout, tylko ich nazwy).

Agent nie dostaje tokena do klastra ani gita. Bramki (system/architecture, sdlc, platforma) i wyrocznia
(scenarios) są chronione w serwerze warsztatu, nie w prompcie.

Użycie:
  python3 sdlc/agent.py prompt --title T --body B        # .sdlc/prompt.md
  python3 sdlc/agent.py run                              # uruchamia agenta na .sdlc/prompt.md
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

import a2a
from lib import ROOT, SDLC, STATE, load_json, tokens

PROTECTED = ["system/architecture/", "sdlc/", "platforma/", "scenarios/"]
ATTEMPT = int(os.environ.get("ATTEMPT", "1"))
TIMEOUT = int(os.environ.get("AGENT_TIMEOUT", "1500"))
BASE = os.environ.get("BASE_BRANCH", "main")


def build_prompt(title: str, body: str) -> str:
    route = load_json(STATE / "route.json")
    docs = [d["path"] for d in route["adrs"] + route["incidents"]]
    attached = "\n\n".join(f"--- {p} ---\n{(ROOT / p).read_text(encoding='utf-8')}" for p in docs)
    feedback_file = STATE / "feedback.md"
    rework = ""
    if ATTEMPT > 1 and feedback_file.exists():
        rework = f"""
## This is a rework (attempt {ATTEMPT})

Your previous change did not pass the factory's quality control. The report is below. Do not weaken
tests and do not bypass gates: the test-weakening detector blocks such changes. Fix the code so that
it meets the requirement from the work order. Your previous changes are still in the repository.

{feedback_file.read_text(encoding="utf-8")}
"""
    return f"""Work order: {title}

{body}

## Where you work

Routing pointed to module `{route['module']}` ({route['path']}), because {route['reason']}.
Blast radius: {', '.join(route['blast_radius']) or 'only this module'}.
Critical path within reach: {', '.join(route['critical_in_radius']) or 'no'}.

## Context you must take into account

{attached or '(no related ADRs or incidents)'}

## Rules

1. Read AGENTS.md in the repository root (read_file).
2. Change code in `{route['path']}`. Change other modules only when the change cannot work otherwise, and say why.
3. Add tests for every behavior change. The test must check the requirement from the work order.
4. Run run_build and fix everything that is red. Do not finish with a red build.
5. Do not touch {', '.join(PROTECTED)}. The server rejects such writes.
6. At the end, write 3-5 sentences describing the change, in Polish, to the file `.sdlc/pr-body.md` (write_file) and reply with the same description.
{rework}"""


# ---------------------------------------------------------------- sterowniki

def run_kagent(prompt: str, events: Path) -> int:
    """Wykonawca w kagent. Zdarzenia narzędzi zapisuje serwer warsztatu do EVENTS_FILE; my dopisujemy odpowiedź."""
    try:
        answer = a2a.send(os.environ.get("AGENT_NAME", "wykonawca"), prompt, timeout=TIMEOUT)
    except Exception as err:
        events.write_text(json.dumps({"type": "agent.error", "error": str(err)}, ensure_ascii=False) + "\n")
        print(f"wykonawca: {err}", file=sys.stderr)
        return 1
    events.write_text(json.dumps({"type": "agent.answer", "text": answer[:4000]}, ensure_ascii=False) + "\n")
    print(answer)
    body = STATE / "pr-body.md"
    if not body.exists():
        body.write_text(answer.strip() + "\n", encoding="utf-8")
    return 0


def run_replay(prompt: str, events: Path) -> int:
    """Tryb awaryjny na słabe Wi-Fi: nagrana łatka zamiast modelu.

    Łatkę wybieramy po słowach ze zlecenia ORAZ po module z routingu. Dzięki temu nawet
    bez modelu widać, że lepszy kontekst daje lepszą zmianę.
    """
    # REPLAY_MODULE nadpisuje routing: tak odtwarzamy „naiwną” zmianę od człowieka w złym module (lekcja 6).
    module = os.environ.get("REPLAY_MODULE") or load_json(STATE / "route.json")["module"]
    words = set(tokens(prompt))
    for replay in load_json(SDLC / "replays" / "index.json")["replays"]:
        same_attempt = replay.get("attempt", 1) == min(ATTEMPT, 2)
        module_ok = ATTEMPT > 1 or replay["module"] == module
        if set(tokens(" ".join(replay["match"]))) & words and same_attempt and module_ok:
            patch = SDLC / "replays" / replay["patch"]
            events.write_text(json.dumps({"type": "replay", "patch": replay["patch"], "note": replay["note"]}, ensure_ascii=False) + "\n")
            (STATE / "pr-body.md").write_text(replay["note"] + "\n\n_(tryb replay: nagrana zmiana, bez modelu)_\n", encoding="utf-8")
            print(f"replay: {replay['patch']} (próba {ATTEMPT})")
            if ATTEMPT > 1:
                # nagranie poprawki to pełna zmiana względem main, więc zaczynamy od czystego main
                subprocess.run(["git", "checkout", BASE, "--", "system"], cwd=ROOT)
                subprocess.run(["git", "clean", "-fdq", "system"], cwd=ROOT)
            return subprocess.run(["git", "apply", "--whitespace=nowarn", str(patch)], cwd=ROOT).returncode
    print("replay: brak nagrania dla tego zlecenia i modułu", file=sys.stderr)
    return 1


DRIVERS = {"kagent": run_kagent, "replay": run_replay}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("prompt")
    p.add_argument("--title", required=True)
    p.add_argument("--body", default="")
    sub.add_parser("run")
    args = parser.parse_args()

    if args.cmd == "prompt":
        prompt = build_prompt(args.title, args.body)
        STATE.mkdir(exist_ok=True)
        (STATE / "prompt.md").write_text(prompt, encoding="utf-8")
        print(prompt)
    else:
        agent = os.environ.get("AGENT", "kagent")
        prompt = (STATE / "prompt.md").read_text(encoding="utf-8")
        code = DRIVERS[agent](prompt, STATE / "agent-events.jsonl")
        print(f"agent {agent} zakończył z kodem {code}")
        sys.exit(code)


if __name__ == "__main__":
    main()
