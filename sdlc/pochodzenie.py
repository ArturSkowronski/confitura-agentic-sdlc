"""Pochodzenie zmiany (GitHub Actions, finał): czy kod w PR jest dokładnie tym, co przeszło przez fabrykę.

Job w Actions działa poza klastrem i poza zasięgiem agenta. Narzędzia i klucz publiczny bierze z main,
nigdy z gałęzi PR. Sprawdza:

  granice     gałąź agent/* nie dotyka bramek, linii, wyroczni ani workflowów (.github/)
  księga      .fabryka/<zlecenie>/ledger.jsonl: łańcuch hashy cały
  podpis      cosign verify-blob kluczem fabryki z main (platforma/linia/cosign/cosign.pub)
  commit      commit z księgi (git.commit) jest przodkiem HEAD, a po nim zmienia się tylko .fabryka/:
              kod, który przeszedł bramki w klastrze, to kod, który trafi do main
  linia       hash konfiguracji linii z księgi kontra main (ostrzeżenie: main mógł się ruszyć)

PR człowieka (gałąź spoza agent/*) bez księgi przechodzi z adnotacją: to nie jest zmiana fabryki.

Użycie:
  python3 sdlc/pochodzenie.py --base origin/main --head HEAD --branch agent/issue-12 [--pub cosign.pub]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

import ledger
from factory import LINE_FILES
from lib import ROOT, git, summary_md

GATES = (".github/", "sdlc/", "platforma/", "scenarios/", "system/architecture/")


def changed(base: str, head: str) -> list[str]:
    return [p for p in git("diff", "--name-only", f"{base}...{head}").splitlines() if p]


def boundary(files: list[str], branch: str) -> list[str]:
    if not branch.startswith("agent/"):
        return []
    return [f for f in files if f.startswith(GATES)]


def ledgers(files: list[str]) -> list[str]:
    return sorted(f for f in files if f.startswith(".fabryka/") and f.endswith("/ledger.jsonl"))


def commit_matches(sha: str, head: str) -> tuple[bool, str]:
    """Commit z księgi ma być przodkiem HEAD, a po nim wolno dopisać tylko .fabryka/."""
    if subprocess.run(["git", "merge-base", "--is-ancestor", sha, head], cwd=ROOT).returncode != 0:
        return False, f"commit {sha[:10]} z księgi nie jest w historii PR: kod zmieniono po przejściu przez fabrykę"
    after = [p for p in git("diff", "--name-only", sha, head).splitlines() if p]
    foreign = [p for p in after if not p.startswith(".fabryka/")]
    if foreign:
        return False, f"po commicie z księgi zmieniono kod: {', '.join(foreign[:5])}"
    return True, f"kod PR = commit {sha[:10]}, który przeszedł bramki fabryki"


def line_drift(records: list[dict], base: str) -> list[str]:
    config = next((r["data"] for r in records if r["type"] == "line.config"), None)
    if not config:
        return ["księga nie ma hasha konfiguracji linii"]
    drift = []
    for name in LINE_FILES:
        try:
            now = hashlib.sha256(subprocess.run(["git", "show", f"{base}:{name}"], cwd=ROOT, capture_output=True,
                                                check=True).stdout).hexdigest()[:10]
        except subprocess.CalledProcessError:
            now = "brak"
        if config.get("parts", {}).get(name) not in (None, now):
            drift.append(name)
    return drift


def signature(path: Path, pub: Path) -> tuple[bool, str]:
    bundle = path.with_name("ledger.sigstore.json")
    if not bundle.exists():
        return False, "brak podpisu księgi (ledger.sigstore.json)"
    try:
        proc = subprocess.run(["cosign", "verify-blob", "--key", str(pub), "--bundle", str(bundle), "--insecure-ignore-tlog",
                               str(path)], capture_output=True, text=True)
    except FileNotFoundError:
        return False, "brak cosign w środowisku"
    return proc.returncode == 0, "podpis kluczem fabryki OK" if proc.returncode == 0 else f"podpis nie pasuje: {proc.stderr.strip()[-200:]}"


def check(base: str, head: str, branch: str, pub: Path) -> tuple[bool, list[str]]:
    files = changed(base, head)
    lines, ok = [], True

    crossed = boundary(files, branch)
    if crossed:
        ok = False
        lines.append(f"❌ granice: gałąź agenta zmienia bramki albo workflowy: {', '.join(crossed[:8])}")
    elif branch.startswith("agent/"):
        lines.append("✅ granice: bez zmian w bramkach, linii, wyroczni i .github/")

    found = ledgers(files)
    if not found:
        if branch.startswith("agent/"):
            return False, lines + ["❌ księga: zmiana agenta bez księgi fabryki (.fabryka/<zlecenie>/ledger.jsonl)"]
        return ok, lines + ["ℹ️ PR spoza fabryki: bez księgi, pochodzenie sprawdza review człowieka"]

    for name in found:
        path = ROOT / name
        records = ledger.read(path)
        chain_ok, chain = ledger.verify(path)
        sig_ok, sig = signature(path, pub)
        commit = next((r["data"] for r in reversed(records) if r["type"] == "git.commit"), None)
        code_ok, code = commit_matches(commit["sha"], head) if commit else (False, "księga nie ma zdarzenia git.commit")
        ok = ok and chain_ok and sig_ok and code_ok
        lines += [f"**{name}**", f"{'✅' if chain_ok else '❌'} łańcuch: {chain}", f"{'✅' if sig_ok else '❌'} {sig}",
                  f"{'✅' if code_ok else '❌'} {code}"]
        drift = line_drift(records, base)
        lines.append("✅ linia: konfiguracja z księgi = main" if not drift else
                     f"⚠️ linia: main zmienił się od przebiegu ({', '.join(drift)}); przebieg jest z innej wersji bramek")
        trace = next((r["data"].get("url") for r in records if r["type"] == "trace"), "")
        if trace:
            lines.append(f"🔭 ślad przebiegu: {trace}")
    return ok, lines


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--base", required=True)
    parser.add_argument("--head", default="HEAD")
    parser.add_argument("--branch", required=True)
    parser.add_argument("--pub", default=str(ROOT / "platforma" / "linia" / "cosign" / "cosign.pub"))
    args = parser.parse_args()
    ok, lines = check(args.base, args.head, args.branch, Path(args.pub))
    report = f"### 🔏 Pochodzenie zmiany: {'✅' if ok else '❌'}\n\n" + "\n".join(f"- {l}" if not l.startswith("**") else f"\n{l}" for l in lines)
    print(report)
    summary_md(report)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
