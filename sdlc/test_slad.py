"""Testy śladu bez Jaegera: sztuczny odbiornik OTLP/HTTP w wątku."""

import json
import threading
import unittest
from http.server import BaseHTTPRequestHandler, HTTPServer

import slad

ENV = {"TRACEPARENT": "00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01", "FABRYKA_RUN": "fabryka-rabat-x1",
       "FABRYKA_NODE": "fabryka-rabat-x1[5].poprawka[4].kontrola.build", "ZLECENIE": "rabat", "ATTEMPT": "2"}


class FakeCollector(BaseHTTPRequestHandler):
    seen = []

    def do_POST(self):
        FakeCollector.seen.append((self.path, json.loads(self.rfile.read(int(self.headers["Content-Length"])))))
        self.send_response(200)
        self.send_header("Content-Length", "2")
        self.end_headers()
        self.wfile.write(b"{}")

    def log_message(self, *args):
        pass


class SladTest(unittest.TestCase):
    def test_step_name_is_readable(self):
        self.assertEqual(slad.step_name(ENV["FABRYKA_NODE"], ENV["FABRYKA_RUN"], "2"), "próba 2 · kontrola.build")
        self.assertEqual(slad.step_name("fabryka-rabat-x1[2].wykonawca[0].run", "fabryka-rabat-x1"), "próba 1 · wykonawca")

    def test_steps_hang_under_one_root_per_run(self):
        step = slad.Step(ENV)
        other = slad.Step({**ENV, "FABRYKA_NODE": "fabryka-rabat-x1[0].przygotuj[0].run"})
        self.assertEqual(slad.step_span(step, 0, 1, 0)["parentSpanId"], slad.step_span(other, 0, 1, 0)["parentSpanId"])
        root = slad.root_span(step, 0, 10, "Failed")
        self.assertEqual(root["spanId"], step.root_id)
        self.assertEqual((root["parentSpanId"], root["name"], root["status"]["code"]), ("", "zlecenie rabat", 2))

    def test_traceparent_keeps_trace_and_points_to_step_span(self):
        step = slad.Step(ENV)
        tp = slad.parse_traceparent(step.traceparent())
        self.assertEqual(tp[0], "4bf92f3577b34da6a3ce929d0e0e4736")
        self.assertEqual(tp[1], step.span_id)
        self.assertEqual(step.span_id, slad.Step(ENV).span_id, "trap i A2A muszą wskazać ten sam span")

    def test_without_traceparent_nothing_is_propagated(self):
        self.assertEqual(slad.Step({}).traceparent(), "")
        self.assertIsNone(slad.parse_traceparent("garbage"))

    def test_rejected_tool_calls_are_errors(self):
        step = slad.Step(ENV)
        events = [{"ts": "2026-09-23T10:00:00Z", "type": "tool.call", "data": {"tool": "run_build", "exit_code": 0, "seconds": 12.5}},
                  {"ts": "2026-09-23T10:00:13Z", "type": "holdout.peek", "data": {"tool": "read_file", "path": "scenarios/rabat/X.java"}}]
        build, peek = slad.tool_spans(step, events)
        self.assertEqual(build["parentSpanId"], step.span_id)
        self.assertEqual(int(build["endTimeUnixNano"]) - int(build["startTimeUnixNano"]), 12_500_000_000)
        self.assertEqual(build["status"]["code"], 1)
        self.assertEqual(peek["status"]["code"], 2)
        self.assertIn("scenarios/rabat/X.java", peek["name"])

    def test_export_posts_otlp_json(self):
        server = HTTPServer(("127.0.0.1", 0), FakeCollector)
        threading.Thread(target=server.serve_forever, daemon=True).start()
        old = slad.ENDPOINT
        slad.ENDPOINT = f"http://127.0.0.1:{server.server_port}"
        try:
            step = slad.Step(ENV)
            self.assertTrue(slad.export([slad.step_span(step, 1_000, 2_000_000_000, 1)]))
        finally:
            slad.ENDPOINT = old
            server.shutdown()
        path, body = FakeCollector.seen[-1]
        self.assertEqual(path, "/v1/traces")
        sent = body["resourceSpans"][0]["scopeSpans"][0]["spans"][0]
        self.assertEqual(sent["parentSpanId"], slad.Step(ENV).root_id)
        self.assertEqual(sent["traceId"], "4bf92f3577b34da6a3ce929d0e0e4736")
        self.assertEqual(sent["status"]["code"], 2)

    def test_export_never_raises(self):
        old = slad.ENDPOINT
        slad.ENDPOINT = "http://127.0.0.1:9"
        try:
            self.assertFalse(slad.export([slad.step_span(slad.Step(ENV), 0, 1, 0)]))
        finally:
            slad.ENDPOINT = old


if __name__ == "__main__":
    unittest.main()
