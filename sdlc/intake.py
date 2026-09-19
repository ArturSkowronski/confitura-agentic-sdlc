"""Przyjęcie zlecenia (lekcja 4): fabryka nie przyjmuje zlecenia bez specyfikacji.

W fabryce oprogramowania ludzie piszą specyfikacje, a agenci resztę. Dlatego pierwsza bramka
stoi przed agentem: zlecenie musi mieć kryteria akceptacji. Jeśli ich nie ma, fabryka odsyła je
z pytaniami, zamiast zgadywać. Sprawdzenie jest deterministyczne. Agent `przyjecie` (kagent, przez A2A)
tylko formułuje pytania, nie decyduje o przyjęciu.

Użycie:
  python3 sdlc/intake.py --title T --body B [--out-md plik]
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import a2a
from lib import STATE, covered_by_scenarios, load_json, outputs, stem, summary_md, tokens, write_json

CRITERIA = re.compile(r"(?im)^\s*(#+\s*)?(kryteria|acceptance criteria|given|zakładając|scenariusz)\b")
CHECKLIST = re.compile(r"(?m)^\s*[-*]\s+(\[[ x]\]\s+)?\S")
PLACEHOLDER = re.compile(r"(?i)\[twoje issue\]|zmień tytuł")



def assess(title: str, body: str) -> dict:
    problems = []
    if PLACEHOLDER.search(f"{title}\n{body}"):
        problems.append("zlecenie to nadal szablon: zmień tytuł i opis na własny pomysł")
    if not CRITERIA.search(body):
        problems.append("brak sekcji z kryteriami akceptacji (np. „Kryteria:”)")
    elif len(CHECKLIST.findall(body)) < 2:
        problems.append("kryteria mają mniej niż dwa punkty")
    if len(body.split()) < 12:
        problems.append("opis ma mniej niż 12 słów")
    route_file = STATE / "route.json"
    if route_file.exists():
        route = load_json(route_file)
        # Yield spada z rozmiarem zlecenia: tytuł nazywający pojęcia dwóch modułów-właścicieli to zwykle dwa zlecenia.
        # Liczy się tytuł, nie opis: opis może wspominać koszyk, a zmiana i tak dotyczy rabatu.
        named = set(tokens(title))
        owners = [c for c in route["candidates"] if named & {stem(w) for w in c["owned"]}]
        if len(owners) > 1:
            problems.append("zlecenie dotyka pojęć z kilku modułów (" + ", ".join(c["module"] for c in owners)
                            + "): podziel je na mniejsze")
        elif not route["confident"]:
            problems.append("routing nie wie, do którego modułu to należy: doprecyzuj albo podziel zlecenie")
    return {"accepted": not problems, "problems": problems, "has_scenarios": covered_by_scenarios(title)}


def questions(title: str, body: str) -> str:
    try:
        return a2a.send("przyjecie", f"Title: {title}\n\nDescription:\n{body}", timeout=120).strip()
    except Exception as err:  # pytania to uprzejmość, nie bramka
        print(f"intake: agent przyjecie nie odpowiedział ({err})", file=sys.stderr)
    return ("1. Jakie dane wejściowe i jaki wynik oczekujesz w typowym przypadku (z liczbami)?\n"
            "2. Co ma się stać na granicy i w przypadku brzegowym?\n"
            "3. Jak system ma się zachować przy błędzie lub niepoprawnych danych?")


def markdown(result: dict, asked: str) -> str:
    if result["accepted"]:
        note = "" if result["has_scenarios"] else (
            "\n\n⚠️ Dla tego zlecenia nie ma scenariuszy holdout. Fabryka je zbuduje, ale nie wypuści bez człowieka.")
        return "### 📥 Przyjęcie zlecenia: ✅ przyjęte na linię" + note
    return "\n".join([
        "### 📥 Przyjęcie zlecenia: ↩️ odesłane",
        "",
        "Fabryka nie zgaduje wymagań. Czego brakuje:",
        *[f"- {p}" for p in result["problems"]],
        "",
        "Pytania, po których da się napisać kryteria:",
        "",
        asked,
        "",
        "Uzupełnij plik zlecenia (sekcja **Kryteria:** z listą punktów) i wyślij je na linię jeszcze raz.",
    ])


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--title", required=True)
    parser.add_argument("--body", default="")
    parser.add_argument("--out-md")
    args = parser.parse_args()

    result = assess(args.title, args.body)
    text = markdown(result, "" if result["accepted"] else questions(args.title, args.body))
    write_json(STATE / "intake.json", result)
    if args.out_md:
        Path(args.out_md).write_text(text, encoding="utf-8")
    print(text)
    summary_md(text)
    outputs(accepted=str(result["accepted"]).lower(), has_scenarios=str(result["has_scenarios"]).lower())


if __name__ == "__main__":
    main()
