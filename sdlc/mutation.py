"""Testy mutacyjne tylko na klasach zmienionych w PR (stacja 3).

Zielony build dowodzi tylko tego, że model zgadza się sam ze sobą. PIT wstrzykuje błędy
do zmienionych klas i sprawdza, czy testy to zauważą. Mierzy testy, nie kod.

Użycie:
  python3 sdlc/mutation.py --base origin/main --head HEAD [--threshold 60]
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from collections import defaultdict

from lib import ROOT, SYSTEM, git, outputs, summary_md

MUTATOR_PL = {
    "ConditionalsBoundaryMutator": "zmiana granicy warunku (< na <=)",
    "NegateConditionalsMutator": "odwrócenie warunku",
    "MathMutator": "zmiana operatora arytmetycznego",
    "EmptyObjectReturnValsMutator": "zwrot pustego obiektu",
    "NullReturnValsMutator": "zwrot null",
    "VoidMethodCallMutator": "usunięcie wywołania metody",
    "PrimitiveReturnsMutator": "zwrot 0",
    "BooleanTrueReturnValsMutator": "zwrot true",
    "BooleanFalseReturnValsMutator": "zwrot false",
    "IncrementsMutator": "zmiana inkrementacji",
}


def changed_classes(base: str, head: str) -> dict[str, list[str]]:
    by_module = defaultdict(list)
    for path in git("diff", "--name-only", "--diff-filter=AM", f"{base}...{head}").splitlines():
        match = re.match(r"system/([\w-]+)/src/main/java/(.+)\.java$", path)
        if match:
            by_module[match.group(1)].append(match.group(2).replace("/", "."))
    return dict(by_module)


def mvn(*args: str) -> int:
    return subprocess.run(["mvn", "-B", "-q", *args], cwd=SYSTEM).returncode


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--base", required=True)
    parser.add_argument("--head", default="HEAD")
    parser.add_argument("--threshold", type=int, default=60)
    args = parser.parse_args()

    targets = changed_classes(args.base, args.head)
    if not targets:
        text = "### 🧬 Mutacje\n\nBrak zmienionych klas produkcyjnych, nie ma czego mutować."
        print(text)
        summary_md(text)
        outputs(score="n/a")
        return

    if mvn("install", "-DskipTests") != 0:
        sys.exit("build nie przeszedł, mutacje pominięte")
    killed = total = 0
    survivors = []
    for module, classes in targets.items():
        mvn("-pl", module, "org.pitest:pitest-maven:mutationCoverage",
            f"-DtargetClasses={','.join(classes)}", "-DtargetTests=pl.confitura.shop.*")
        report = SYSTEM / module / "target" / "pit-reports" / "mutations.xml"
        if not report.exists():
            continue
        for m in ET.parse(report).getroot():
            total += 1
            if m.get("detected") == "true":
                killed += 1
            else:
                mutator = m.findtext("mutator").rsplit(".", 1)[-1]
                survivors.append({
                    "file": f"system/{module}/src/main/java/{m.findtext('mutatedClass').replace('.', '/')}.java",
                    "line": m.findtext("lineNumber"),
                    "what": MUTATOR_PL.get(mutator, mutator),
                    "status": m.get("status"),
                })
    score = round(100 * killed / total) if total else 100
    ok = score >= args.threshold
    lines = [f"### 🧬 Mutacje: {'✅' if ok else '❌'} {score}% zabitych (próg {args.threshold}%)", "",
             f"Klasy: {', '.join(c for cs in targets.values() for c in cs)}. Mutantów: {total}, zabitych: {killed}."]
    if survivors:
        lines += ["", "Przeżyły (testy tego nie zauważą):", "", "| plik | linia | mutacja |", "|---|---|---|"]
        lines += [f"| `{s['file'].split('/')[-1]}` | {s['line']} | {s['what']} |" for s in survivors[:10]]
    text = "\n".join(lines)
    print(text)
    summary_md(text)
    outputs(score=score)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
