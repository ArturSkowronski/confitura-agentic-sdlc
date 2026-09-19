"""Warsztat agenta: pięć operacji na kopii repozytorium w /work/repo. Bez zależności poza biblioteką standardową.

Granice, których agent nie może obejść, są tutaj, a nie w prompcie:
  PROTECTED_PATHS  zapis odrzucony (bramki, linia, wyrocznia)          → zdarzenie gate.tamper_attempt
  HIDDEN_PATHS     odczyt i listowanie odrzucone (scenariusze holdout) → zdarzenie holdout.peek
Każde wywołanie narzędzia trafia do EVENTS_FILE (jsonl), skąd linia przepisuje je do księgi.
"""

from __future__ import annotations

import json
import os
import subprocess
import time
from pathlib import Path


class Workspace:
    def __init__(self, root: str | Path, protected: list[str], hidden: list[str], events_file: str | Path | None = None):
        self.root = Path(root).resolve()
        self.protected = [p.strip("/") for p in protected if p.strip()]
        self.hidden = [p.strip("/") for p in hidden if p.strip()]
        self.events_file = Path(events_file) if events_file else None

    @classmethod
    def from_env(cls) -> "Workspace":
        split = lambda v: [x for x in os.environ.get(v, "").replace(",", " ").split() if x]
        return cls(os.environ.get("WORK_DIR", "/work/repo"), split("PROTECTED_PATHS"), split("HIDDEN_PATHS"),
                   os.environ.get("EVENTS_FILE"))

    # ---------------------------------------------------------------- pomocnicze

    def _rel(self, path: str) -> str:
        full = (self.root / path).resolve()
        if full != self.root and self.root not in full.parents:
            raise ValueError(f"Rejected: {path} escapes the repository")
        return str(full.relative_to(self.root)) if full != self.root else ""

    @staticmethod
    def _under(rel: str, prefixes: list[str]) -> str | None:
        for prefix in prefixes:
            if rel == prefix or rel.startswith(prefix + "/"):
                return prefix
        return None

    def event(self, event_type: str, **data) -> None:
        record = {"ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "type": event_type, "data": data}
        if self.events_file:
            self.events_file.parent.mkdir(parents=True, exist_ok=True)
            with self.events_file.open("a", encoding="utf-8") as fh:
                fh.write(json.dumps(record, ensure_ascii=False) + "\n")

    # ---------------------------------------------------------------- narzędzia

    def list_files(self, path: str = ".") -> str:
        rel = self._rel(path)
        if self._under(rel, self.hidden):
            self.event("holdout.peek", tool="list_files", path=rel)
            return f"Rejected: {rel or '/'} is out of the agent's reach"
        base = self.root / rel
        if not base.is_dir():
            return f"No such directory: {rel}"
        lines = []
        for entry in sorted(base.iterdir()):
            r = str(entry.relative_to(self.root))
            if entry.name in {".git", "target", "__pycache__"} or self._under(r, self.hidden):
                continue
            lines.append(r + ("/" if entry.is_dir() else ""))
        self.event("tool.call", tool="list_files", path=rel)
        return "\n".join(lines) or "(empty directory)"

    def read_file(self, path: str) -> str:
        rel = self._rel(path)
        if self._under(rel, self.hidden):
            self.event("holdout.peek", tool="read_file", path=rel)
            return f"Rejected: {rel} is out of the agent's reach"
        full = self.root / rel
        if not full.is_file():
            return f"No such file: {rel}"
        self.event("tool.call", tool="read_file", path=rel)
        return full.read_text(encoding="utf-8", errors="replace")

    def write_file(self, path: str, content: str) -> str:
        rel = self._rel(path)
        blocked = self._under(rel, self.protected) or self._under(rel, self.hidden)
        if blocked:
            self.event("gate.tamper_attempt", tool="write_file", path=rel, blocked=True)
            return f"Rejected: {rel} is a protected path ({blocked}/). Gates and the oracle are not changed by the agent."
        full = self.root / rel
        full.parent.mkdir(parents=True, exist_ok=True)
        full.write_text(content, encoding="utf-8")
        self.event("tool.call", tool="write_file", path=rel, bytes=len(content.encode("utf-8")))
        return f"Written {rel} ({len(content.splitlines())} lines)"

    def run_build(self, module: str = "") -> str:
        """`mvn -B -q verify` w system/ (albo w jednym module). Zwraca kod i ogon logu."""
        cwd = self.root / "system" / module if module else self.root / "system"
        if not (cwd / "pom.xml").is_file():
            return f"No pom.xml in {cwd.relative_to(self.root)}"
        args = ["mvn", "-B", "-q", "verify"]
        if module:
            args = ["mvn", "-B", "-q", "verify", "-pl", module, "-am"]
            cwd = self.root / "system"
        started = time.time()
        try:
            proc = subprocess.run(args, cwd=cwd, capture_output=True, text=True, timeout=int(os.environ.get("BUILD_TIMEOUT", "600")))
            code, output = proc.returncode, (proc.stdout + proc.stderr)
        except subprocess.TimeoutExpired:
            code, output = 124, "build timed out"
        except FileNotFoundError:
            code, output = 127, "mvn is not available in this container"
        tail = "\n".join(output.strip().splitlines()[-60:])
        self.event("tool.call", tool="run_build", module=module, exit_code=code, seconds=round(time.time() - started, 1))
        return f"exit={code} ({'green' if code == 0 else 'red'})\n{tail}"

    def git_diff(self) -> str:
        proc = subprocess.run(["git", "status", "--porcelain", "--untracked-files=all"], cwd=self.root, capture_output=True, text=True)
        diff = subprocess.run(["git", "diff"], cwd=self.root, capture_output=True, text=True).stdout
        self.event("tool.call", tool="git_diff")
        return f"Changed files:\n{proc.stdout or '(none)'}\n\n{diff[:20000]}"
