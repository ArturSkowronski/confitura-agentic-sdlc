"""Testy fabryki na GitHubie bez GitHuba: sztuczne API REST/GraphQL w wątku."""

import json
import os
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

import github


class FakeGitHub(BaseHTTPRequestHandler):
    calls = []
    reject_inline = False
    existing_pr = None

    def _reply(self, code, data):
        payload = json.dumps(data).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def _handle(self, method):
        length = int(self.headers.get("Content-Length") or 0)
        body = json.loads(self.rfile.read(length)) if length else None
        FakeGitHub.calls.append((method, self.path, body))
        path = self.path
        if path.endswith("/reviews") and FakeGitHub.reject_inline and body.get("comments"):
            return self._reply(422, {"message": "line must be part of the diff"})
        if method == "GET" and "/pulls?state=open" in path:
            return self._reply(200, [FakeGitHub.existing_pr] if FakeGitHub.existing_pr else [])
        if method == "GET" and path.endswith("/files?per_page=100"):
            return self._reply(200, [{"filename": "system/pricing-lib/src/main/java/Rabat.java"}])
        if method in ("POST", "PATCH") and "/pulls" in path and not path.endswith("/reviews"):
            return self._reply(201, {"number": 7, "node_id": "PR_7", "html_url": "https://github.com/o/r/pull/7"})
        if path == "/graphql":
            return self._reply(200, {"data": {"enablePullRequestAutoMerge": {"pullRequest": {"number": 7}}}})
        if method == "DELETE":
            return self._reply(404, {"message": "Label does not exist"})
        return self._reply(200, {})

    def do_GET(self):
        self._handle("GET")

    def do_POST(self):
        self._handle("POST")

    def do_PATCH(self):
        self._handle("PATCH")

    def do_DELETE(self):
        self._handle("DELETE")

    def log_message(self, *args):
        pass


def issue(number, labels, pr=False):
    data = {"number": number, "title": f"Zlecenie {number}", "body": "Kryteria:\n- a", "html_url": f"https://x/{number}",
            "labels": [{"name": l} for l in labels]}
    if pr:
        data["pull_request"] = {}
    return data


class GitHubTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = HTTPServer(("127.0.0.1", 0), FakeGitHub)
        threading.Thread(target=cls.server.serve_forever, daemon=True).start()
        github.API = f"http://127.0.0.1:{cls.server.server_port}"
        os.environ.update({"GH_TOKEN": "t0k3n", "GH_REPO": "o/r"})

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()

    def setUp(self):
        FakeGitHub.calls.clear()
        FakeGitHub.reject_inline = False
        FakeGitHub.existing_pr = None

    def test_pick_takes_oldest_untouched_issue_and_skips_prs(self):
        issues = [issue(9, ["fabryka"]), issue(3, ["fabryka", "fabryka:w-toku"]), issue(5, ["fabryka"], pr=True),
                  issue(6, ["fabryka"]), issue(2, ["bug"])]
        self.assertEqual(github.pick(issues)["number"], 6)
        self.assertIsNone(github.pick([issue(1, ["fabryka", "fabryka:odeslane"])]))

    def test_issue_becomes_work_order(self):
        order = github.order(issue(12, ["fabryka"]))
        self.assertEqual((order["name"], order["issue"]), ("issue-12", 12))
        self.assertIn("Kryteria:", order["body"])

    def test_pr_body_closes_issue_and_links_trace(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            (out / "opis.md").write_text("Rabat w pricing-lib.")
            (out / "karta.md").write_text("### 🏭 Karta zlecenia")
            body = github.pr_body(out, 12, "lights-out", "issue-12", "http://j/trace/abc", "http://hala/x")
        self.assertTrue(body.startswith("Closes #12."))
        self.assertIn("lights-out", body)
        self.assertIn("[ślad w Jaegerze](http://j/trace/abc)", body)
        self.assertIn(".fabryka/issue-12/ledger.jsonl", body)

    def test_review_comments_only_for_changed_files(self):
        sarif = {"runs": [{"results": [
            {"ruleId": "DET-004", "level": "error", "message": {"text": "klucz idempotencji"},
             "locations": [{"physicalLocation": {"artifactLocation": {"uri": "a.java"}, "region": {"startLine": 4}}}]},
            {"ruleId": "LLM", "level": "warning", "message": {"text": "poza zmianą"},
             "locations": [{"physicalLocation": {"artifactLocation": {"uri": "b.java"}, "region": {"startLine": 1}}}]}]}]}
        comments = github.review_comments(sarif, {"a.java"})
        self.assertEqual(len(comments), 1)
        self.assertEqual((comments[0]["path"], comments[0]["line"]), ("a.java", 4))
        self.assertIn("🚫 **DET-004**", comments[0]["body"])

    def test_review_falls_back_to_summary_when_inline_rejected(self):
        FakeGitHub.reject_inline = True
        sarif = {"runs": [{"results": [{"ruleId": "R", "level": "note", "message": {"text": "x"},
                                        "locations": [{"physicalLocation": {"artifactLocation": {"uri": "a.java"}, "region": {"startLine": 1}}}]}]}]}
        github.post_review(7, "raport", sarif, {"a.java"})
        reviews = [c for c in FakeGitHub.calls if c[1].endswith("/reviews")]
        self.assertEqual(len(reviews), 2)
        self.assertEqual(reviews[-1][2]["event"], "COMMENT")
        self.assertNotIn("comments", reviews[-1][2])

    def test_publish_lights_out_enables_auto_merge_and_moves_labels(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            (out / "review-2-review.md").write_text("### Review")
            state = github.ROOT / ".sdlc"
            state.mkdir(exist_ok=True)
            existed = (state / "zlecenie.json").read_text() if (state / "zlecenie.json").exists() else None
            (state / "zlecenie.json").write_text(json.dumps({"title": "Rabat 10%"}))
            try:
                github.publish(12, out, "lights-out", "issue-12", "", "")
            finally:
                if existed is None:
                    (state / "zlecenie.json").unlink()
                else:
                    (state / "zlecenie.json").write_text(existed)
        paths = [(m, p) for m, p, _ in FakeGitHub.calls]
        created = next(b for m, p, b in FakeGitHub.calls if m == "POST" and p == "/repos/o/r/pulls")
        self.assertEqual((created["head"], created["base"], created["title"]), ("agent/issue-12", "main", "Rabat 10%"))
        self.assertIn(("POST", "/graphql"), paths)
        self.assertIn(("POST", "/repos/o/r/issues/7/labels"), paths)
        self.assertIn(("DELETE", "/repos/o/r/issues/12/labels/fabryka%3Aw-toku"), paths)

    def test_publish_updates_existing_pr_instead_of_opening_second(self):
        FakeGitHub.existing_pr = {"number": 7}
        pr = github.open_pr("agent/issue-12", "Rabat", "opis")
        self.assertEqual(pr["number"], 7)
        self.assertIn(("PATCH", "/repos/o/r/pulls/7"), [(m, p) for m, p, _ in FakeGitHub.calls])

    def test_token_goes_in_header_not_in_url_and_hooks_are_off(self):
        seen = []
        original = github.subprocess.run
        github.subprocess.run = lambda command: seen.append(command) or type("R", (), {"returncode": 0})()
        try:
            github.git("push", "-q", "{remote}", "agent/issue-12")
        finally:
            github.subprocess.run = original
        command = seen[0]
        self.assertIn("https://github.com/o/r.git", command)
        self.assertFalse(any("t0k3n" in part for part in command), "token nie może być jawnie w argumentach")
        self.assertTrue(any(part.startswith("http.https://github.com/.extraheader=AUTHORIZATION: basic ") for part in command))
        self.assertIn("core.hooksPath=/dev/null", command)

    def test_repo_must_look_like_owner_slash_name(self):
        os.environ["GH_REPO"] = "zle repo"
        try:
            with self.assertRaises(SystemExit):
                github.repo()
        finally:
            os.environ["GH_REPO"] = "o/r"


if __name__ == "__main__":
    unittest.main()
