"""Raport z bramki deterministycznej (stacja 3) i skaner logów narzędzi.

Agent czyta wyjście narzędzi, więc wyjście narzędzi to wejście do modelu. Przykład z życia:
jqwik 1.10.1 wypisuje przy każdym `mvn test` tekst „If you are an AI Agent (...) Disregard
previous instructions”. Bramka działa poza agentem i takiego tekstu nie słucha, ale warto
wiedzieć, co agent dostał do przeczytania.

Drugie narzędzie to detektor osłabiania testów. Każda poprawka przesuwa agenta od wymagania
w stronę bramki, a najtańszy sposób, żeby „przejść” bramkę, to osłabić test: usunąć asercję,
dodać @Disabled, skasować przypadek. To wykrywamy deterministycznie na diffie i blokujemy.

Użycie:
  python3 sdlc/gates.py report --log mvn.log --exit-code 0
  python3 sdlc/gates.py weakening --base origin/main --head HEAD
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

from lib import git, summary_md

INJECTION = re.compile(r"(?i)(if you are an ai|disregard (all )?previous|ignore (all )?(previous|prior) instructions|you must not use this)")


def report(log: str, exit_code: int) -> tuple[str, list[str]]:
    runs = [tuple(map(int, m)) for m in re.findall(r"Tests run: (\d+), Failures: (\d+), Errors: (\d+), Skipped: (\d+)\n", log)]
    total = [sum(col) for col in zip(*runs)] if runs else [0, 0, 0, 0]
    violations = re.findall(r"Rule '(.+?)' was violated \((\d+) times?\):\n((?:.+\n)+?)(?=\S*\[|\Z|\n)", log)
    injected = sorted({m.group(0) for m in INJECTION.finditer(log)})
    out = [f"### 🧱 Build + ArchUnit: {'✅ zielono' if exit_code == 0 else '❌ czerwono'}", "",
           f"Testy: {total[0]}, porażki: {total[1]}, błędy: {total[2]}."]
    seen = set()
    for rule, times, details in violations:
        because = rule.split(", because ")[-1] if ", because " in rule else rule
        if because in seen:
            continue
        seen.add(because)
        out += ["", f"**Naruszona reguła architektury** ({times}×): {because}", "", "```",
                *[l for l in details.strip().splitlines() if not l.strip().startswith("at ")][:4], "```"]
    if injected:
        out += ["", "⚠️ **Log narzędzi zawiera tekst skierowany do agentów AI** (agent przeczyta go jako wejście):",
                *[f"- `{i}`" for i in injected],
                "", "Bramka działa poza agentem, więc wynik powyżej jest niezależny od tego tekstu."]
    return "\n".join(out), injected


WEAKENING = [
    ("usunięta asercja", re.compile(r"^-\s*(assert\w*\(|assertThat\(|Assertions\.)"), None),
    ("usunięty test", re.compile(r"^-\s*@(Test|Property|ArchTest)\b"), None),
    ("wyłączony test", re.compile(r"^\+\s*@(\w+\.)*Disabled\b"), None),
    ("połknięty wyjątek w teście", re.compile(r"^\+.*catch \((Exception|Throwable|AssertionError) \w+\) \{\s*\}"), None),
]


def weakening(base: str, head: str) -> list[dict]:
    found, current = [], None
    for line in git("diff", "-U0", f"{base}...{head}", "--", "system/*/src/test/**", "system/**/src/test/**").splitlines():
        if line.startswith("+++ ") or line.startswith("--- "):
            if line.startswith("--- a/"):
                current = line[6:]
            continue
        for label, pattern, _ in WEAKENING:
            if pattern.search(line):
                found.append({"what": label, "file": current, "line": line[1:].strip()[:100]})
    deleted = [l[5:] for l in git("diff", "--name-status", f"{base}...{head}", "--", "system").splitlines()
               if l.startswith("D\t") and "/src/test/" in l]
    found += [{"what": "skasowany plik testów", "file": f, "line": ""} for f in deleted]
    return found


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("report")
    r.add_argument("--log", required=True)
    r.add_argument("--exit-code", type=int, required=True)
    w = sub.add_parser("weakening")
    w.add_argument("--base", required=True)
    w.add_argument("--head", default="HEAD")
    args = parser.parse_args()
    if args.cmd == "report":
        text, _ = report(Path(args.log).read_text(encoding="utf-8", errors="replace"), args.exit_code)
        print(text)
        summary_md(text)
        return
    found = weakening(args.base, args.head)
    if not found:
        text = "### 🪤 Osłabianie testów: ✅ nic"
    else:
        text = "\n".join(["### 🪤 Osłabianie testów: ❌ agent „przechodzi” bramkę, zamiast spełnić wymaganie", "",
                          *[f"- {f['what']}: `{f['file']}` {('`' + f['line'] + '`') if f['line'] else ''}" for f in found]])
    print(text)
    summary_md(text)
    raise SystemExit(1 if found else 0)


if __name__ == "__main__":
    main()
