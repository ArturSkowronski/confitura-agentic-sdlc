"""Testy klienta A2A bez klastra: sztuczny serwer JSON-RPC w wątku."""

import json
import os
import threading
import unittest
from http.server import BaseHTTPRequestHandler, HTTPServer

import a2a


class FakeKagent(BaseHTTPRequestHandler):
    seen = []

    def do_POST(self):
        body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        FakeKagent.seen.append((self.path, self.headers.get("X-User-Id"), body))
        text = body["params"]["message"]["parts"][0]["text"]
        if text == "błąd":
            result = {"jsonrpc": "2.0", "id": body["id"], "error": {"code": -32603, "message": "model padł"}}
        elif text == "bez artefaktu":
            result = {"jsonrpc": "2.0", "id": body["id"], "result": {"kind": "task", "artifacts": [], "history": [
                {"role": "user", "parts": [{"kind": "text", "text": text}]},
                {"role": "agent", "parts": [{"kind": "text", "text": "z historii"}]}]}}
        else:
            result = {"jsonrpc": "2.0", "id": body["id"], "result": {"kind": "task", "status": {"state": "completed"},
                      "artifacts": [{"parts": [{"kind": "text", "text": f"echo: {text}"}]}]}}
        payload = json.dumps(result).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def log_message(self, *args):
        pass


class A2ATest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = HTTPServer(("127.0.0.1", 0), FakeKagent)
        threading.Thread(target=cls.server.serve_forever, daemon=True).start()
        os.environ["KAGENT_URL"] = f"http://127.0.0.1:{cls.server.server_port}"
        os.environ["A2A_USER"] = "test@warsztat"

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()

    def test_send_returns_artifact_text_and_uses_agent_path(self):
        self.assertEqual(a2a.send("probny", "cześć"), "echo: cześć")
        path, user, body = FakeKagent.seen[-1]
        self.assertEqual(path, "/api/a2a/fabryka/probny/")
        self.assertEqual(user, "test@warsztat")
        self.assertEqual(body["method"], "message/send")

    def test_falls_back_to_last_agent_message(self):
        self.assertEqual(a2a.send("probny", "bez artefaktu"), "z historii")

    def test_error_is_raised(self):
        with self.assertRaises(RuntimeError):
            a2a.send("probny", "błąd")

    def test_extract_text_without_text_raises(self):
        with self.assertRaises(RuntimeError):
            a2a.extract_text({"kind": "task", "status": {"state": "failed"}})


if __name__ == "__main__":
    unittest.main()
