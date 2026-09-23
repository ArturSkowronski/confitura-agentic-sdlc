"""Testy pochodzenia na prawdziwym repo w katalogu tymczasowym, z prawdziwym podpisem cosign (jak w linii)."""

import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

import ledger
import lib
import pochodzenie


def sh(cwd, *args, env=None):
    subprocess.run(args, cwd=cwd, check=True, capture_output=True, env=env)


@unittest.skipUnless(shutil.which("cosign"), "cosign niedostępny")
class PochodzenieTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = root = Path(self.tmp.name)
        sh(root, "git", "init", "-q", "-b", "main")
        sh(root, "git", "config", "user.email", "t@t")
        sh(root, "git", "config", "user.name", "t")
        for name in pochodzenie.LINE_FILES:
            (root / name).parent.mkdir(parents=True, exist_ok=True)
            (root / name).write_text(f"{name}\n")
        (root / "system").mkdir(exist_ok=True)
        (root / "system" / "Rabat.java").write_text("class Rabat {}\n")
        sh(root, "git", "add", "-A")
        sh(root, "git", "commit", "-qm", "main")
        env = {**os.environ, "COSIGN_PASSWORD": ""}
        sh(root, "cosign", "generate-key-pair", env=env)
        self.pub = root / "cosign.pub"
        self._patch = (pochodzenie.ROOT, lib.ROOT)
        pochodzenie.ROOT = lib.ROOT = root

    def tearDown(self):
        pochodzenie.ROOT, lib.ROOT = self._patch
        self.tmp.cleanup()

    def factory_change(self, sign=True):
        """To, co robi linia: commit agenta, księga z hashem linii i commitem, podpis, commit .fabryka/."""
        root = self.root
        sh(root, "git", "switch", "-q", "-c", "agent/issue-12")
        (root / "system" / "Rabat.java").write_text("class Rabat { int percent = 10; }\n")
        sh(root, "git", "commit", "-qam", "agent: rabat")
        sha = subprocess.run(["git", "rev-parse", "HEAD"], cwd=root, capture_output=True, text=True).stdout.strip()
        book = root / ".fabryka" / "issue-12" / "ledger.jsonl"
        parts = {n: __import__("hashlib").sha256((root / n).read_bytes()).hexdigest()[:10] for n in pochodzenie.LINE_FILES}
        ledger.append(book, "line.config", {"hash": "x", "parts": parts})
        ledger.append(book, "git.commit", {"sha": sha, "branch": "agent/issue-12"})
        ledger.append(book, "trace", {"url": "http://localhost:16686/trace/abc"})
        if sign:
            sh(root, "cosign", "sign-blob", "--yes", "--key", "cosign.key", "--tlog-upload=false", "--use-signing-config=false",
               "--bundle", str(book.with_name("ledger.sigstore.json")), str(book), env={**os.environ, "COSIGN_PASSWORD": ""})
        sh(root, "git", "add", ".fabryka")
        sh(root, "git", "commit", "-qm", "fabryka: księga")
        return book

    def run_check(self, branch="agent/issue-12"):
        return pochodzenie.check("main", "HEAD", branch, self.pub)

    def test_factory_change_passes(self):
        self.factory_change()
        ok, lines = self.run_check()
        self.assertTrue(ok, lines)
        self.assertTrue(any("ślad przebiegu" in l for l in lines))

    def test_code_changed_after_gates_fails(self):
        self.factory_change()
        (self.root / "system" / "Rabat.java").write_text("class Rabat { int percent = 99; }\n")
        sh(self.root, "git", "commit", "-qam", "poprawka ręczna po bramkach")
        ok, lines = self.run_check()
        self.assertFalse(ok)
        self.assertTrue(any("po commicie z księgi zmieniono kod" in l for l in lines))

    def test_edited_ledger_fails_chain_and_signature(self):
        book = self.factory_change()
        book.write_text(book.read_text().replace("agent/issue-12", "agent/inna"))
        sh(self.root, "git", "commit", "-qam", "podmiana księgi")
        ok, lines = self.run_check()
        self.assertFalse(ok)
        self.assertTrue(any("❌ łańcuch" in l for l in lines))
        self.assertTrue(any("podpis nie pasuje" in l for l in lines))

    def test_unsigned_ledger_fails(self):
        self.factory_change(sign=False)
        ok, lines = self.run_check()
        self.assertFalse(ok)
        self.assertTrue(any("brak podpisu" in l for l in lines))

    def test_agent_branch_touching_workflows_fails(self):
        self.factory_change()
        (self.root / ".github" / "workflows").mkdir(parents=True)
        (self.root / ".github" / "workflows" / "fabryka.yml").write_text("on: push\n")
        sh(self.root, "git", "add", "-A")
        sh(self.root, "git", "commit", "-qm", "wyłączam bramki")
        ok, lines = self.run_check()
        self.assertFalse(ok)
        self.assertTrue(any("❌ granice" in l for l in lines))

    def test_agent_branch_without_ledger_fails_human_branch_passes(self):
        sh(self.root, "git", "switch", "-q", "-c", "agent/issue-13")
        (self.root / "system" / "Rabat.java").write_text("class Rabat { }\n")
        sh(self.root, "git", "commit", "-qam", "bez księgi")
        self.assertFalse(self.run_check("agent/issue-13")[0])
        ok, lines = self.run_check("feature/reczna")
        self.assertTrue(ok)
        self.assertTrue(any("PR spoza fabryki" in l for l in lines))


if __name__ == "__main__":
    unittest.main()
