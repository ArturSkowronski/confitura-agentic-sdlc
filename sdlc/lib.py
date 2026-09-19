"""Wspólne kawałki platformy. Tylko biblioteka standardowa: działa w każdym kontenerze linii bez pip install."""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SYSTEM = ROOT / "system"
SCENARIOS = ROOT / "scenarios"
SDLC = ROOT / "sdlc"
STATE = ROOT / ".sdlc"


def load_json(path: Path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def policy() -> dict:
    return load_json(SDLC / "policy.json")


def git(*args: str) -> str:
    out = subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True)
    if out.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)}: {out.stderr.strip()}")
    return out.stdout


def modules() -> list[dict]:
    """Katalog modułów (L1): system/<moduł>/module.json plus zależności z pom.xml."""
    found = []
    for descriptor in sorted(SYSTEM.glob("*/module.json")):
        module = load_json(descriptor)
        module["path"] = str(descriptor.parent.relative_to(ROOT))
        pom = (descriptor.parent / "pom.xml").read_text(encoding="utf-8")
        module["depends_on"] = sorted(set(re.findall(r"<artifactId>([\w-]+)</artifactId>", pom)) & _module_names() - {module["name"]})
        found.append(module)
    return found


def _module_names() -> set[str]:
    return {p.parent.name for p in SYSTEM.glob("*/module.json")}


def module_for_path(path: str, catalog: list[dict]) -> dict | None:
    for module in catalog:
        if path.startswith(module["path"] + "/"):
            return module
    return None


# Bardzo prosty „stemmer” dla polskiego: porównujemy pierwsze 5 liter.
# „zamówień”, „zamówienia” i „zamówienie” trafiają w to samo. Wystarczy na warsztat,
# a jest w pełni deterministyczny: ten sam tekst zawsze daje ten sam wynik.
def stem(word: str) -> str:
    return word.lower()[:5]


STOPWORDS = {"dla", "który", "która", "które", "którzy", "jest", "się", "oraz", "albo", "the", "and", "for", "ma", "mają", "nie", "tak", "jak", "niż", "przez"}


def tokens(text: str) -> list[str]:
    words = re.findall(r"[a-ząćęłńóśźż]+", text.lower())
    return [stem(w) for w in words if len(w) >= 3 and w not in STOPWORDS]


def split_camel(name: str) -> list[str]:
    return re.findall(r"[A-Z]?[a-z]+", name)


def outputs(**values) -> None:
    """Wyjścia kroku linii. W Argo Workflows każdy klucz to plik w $OUTPUTS_DIR (outputs.parameters.valueFrom.path).
    Lokalnie drukujemy na stderr."""
    target = os.environ.get("OUTPUTS_DIR")
    if target:
        Path(target).mkdir(parents=True, exist_ok=True)
        for key, value in values.items():
            (Path(target) / key).write_text(str(value), encoding="utf-8")
    else:
        print("\n".join(f"::wyjście:: {k}={v}" for k, v in values.items()), file=sys.stderr)


def summary_md(markdown: str) -> None:
    """Raport kroku w markdown. Trafia do $SUMMARY_FILE (fragment komentarza w karcie zlecenia)."""
    target = os.environ.get("SUMMARY_FILE")
    if target:
        with open(target, "a", encoding="utf-8") as fh:
            fh.write(markdown + "\n")


def scenarios_for(work_order: str) -> list[dict]:
    """Scenariusze holdout obowiązujące zlecenie: zawsze regresja plus te pasujące do tytułu."""
    index = SCENARIOS / "index.json"
    if not index.exists():
        return []
    words = set(tokens(work_order))
    chosen = []
    for scenario in load_json(index)["scenarios"]:
        if scenario.get("always") or words & set(tokens(" ".join(scenario.get("match", [])))):
            chosen.append(scenario)
    return chosen


def covered_by_scenarios(work_order: str) -> bool:
    """Czy zlecenie ma własne scenariusze (poza regresją). Bez nich fabryka nie gasi światła."""
    return any(not s.get("always") for s in scenarios_for(work_order))
