"""Ślad przebiegu w OpenTelemetry: jeden trace na zlecenie, od węzła Argo do wywołania modelu.

Argo Workflows (4.x, z OTEL_EXPORTER_OTLP_ENDPOINT na kontrolerze) zakłada trace dla przebiegu
i wstrzykuje do kontenera kroku TRACEPARENT. Bierzemy z niego tylko trace id: span, na który wskazuje,
Argo 4.1 nie eksportuje. Ten moduł dokłada to, czego Argo nie wie:

  korzeń        „zlecenie <nazwa>” od startu do końca przebiegu, wysyłany w onExit (także po awarii)
  span kroku    czytelna nazwa („próba 2 · kontrola.build”), zlecenie, kod wyjścia; dziecko korzenia
  traceparent   kontekst dla A2A: agent kagent zagnieżdża swoje spany (invoke_agent, generate_content,
                execute_tool) pod krokiem, który go wołał
  narzędzia     zdarzenia serwera warsztatu (/work/events.jsonl) jako spany-dzieci kroku `wykonawca`,
                razem z odrzuconymi próbami (gate.tamper_attempt, holdout.peek) oznaczonymi jako błąd

Eksport to OTLP/HTTP JSON do Jaegera, best effort: brak Jaegera nigdy nie zatrzymuje linii.
Identyfikatory spanów są deterministyczne (hash węzła), więc trap w kroku i A2A w środku kroku
wskazują ten sam span bez przekazywania stanu między procesami.

Użycie (w kroku linii, zmienne TRACEPARENT, FABRYKA_RUN i FABRYKA_NODE ustawia szablon):
  python3 sdlc/slad.py traceparent                     # kontekst dla A2A: 00-<trace>-<span kroku>-01
  python3 sdlc/slad.py krok --start NS --exit 0        # span kroku
  python3 sdlc/slad.py narzedzia --events F            # spany narzędzi warsztatu pod krokiem
  python3 sdlc/slad.py korzen --start 2026-09-23T10:00:00Z --status Succeeded   # onExit
  python3 sdlc/slad.py url                             # link do śladu w Jaegerze
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ENDPOINT = os.environ.get("FABRYKA_OTLP_HTTP", "http://jaeger.fabryka.svc:4318")
UI = os.environ.get("FABRYKA_JAEGER_UI", "http://localhost:16686")
SERVICE = "fabryka-linia"


def parse_traceparent(value: str | None) -> tuple[str, str] | None:
    match = re.fullmatch(r"00-([0-9a-f]{32})-([0-9a-f]{16})-[0-9a-f]{2}", (value or "").strip())
    return (match.group(1), match.group(2)) if match else None


def span_id(*parts: str) -> str:
    return hashlib.sha256("/".join(parts).encode()).hexdigest()[:16]


def step_name(node: str, run: str, attempt: str = "1") -> str:
    """fabryka-rabat-x[5].poprawka[3].kontrola.build → „próba 2 · kontrola.build”."""
    rest = node[len(run):] if node.startswith(run) else node
    parts = [re.sub(r"\[\d+\]", "", p) for p in rest.strip(".[]0123456789").split(".")]
    parts = [p for p in parts if p and p not in ("run", "poprawka")]
    return f"próba {attempt} · {'.'.join(parts) or node}"


class Step:
    """Kontekst bieżącego kroku z env. Bez TRACEPARENT (np. lokalnie) nic nie eksportuje."""

    def __init__(self, env=os.environ):
        self.parent = parse_traceparent(env.get("TRACEPARENT"))
        self.run = env.get("FABRYKA_RUN", "lokalnie")
        self.node = env.get("FABRYKA_NODE") or env.get("ARGO_NODE_ID", "krok")
        self.attrs = {"fabryka.run": self.run, "fabryka.zlecenie": env.get("ZLECENIE", ""),
                      "fabryka.proba": env.get("ATTEMPT", "1"), "fabryka.agent": env.get("AGENT", ""),
                      "argo.node": self.node}

    @property
    def trace_id(self) -> str | None:
        return self.parent[0] if self.parent else None

    @property
    def span_id(self) -> str:
        return span_id(self.run, self.node)

    @property
    def root_id(self) -> str:
        return span_id(self.run, "zlecenie")

    def traceparent(self) -> str:
        return f"00-{self.trace_id}-{self.span_id}-01" if self.parent else ""


def _attr(key: str, value) -> dict:
    if isinstance(value, bool):
        return {"key": key, "value": {"boolValue": value}}
    if isinstance(value, int):
        return {"key": key, "value": {"intValue": str(value)}}
    return {"key": key, "value": {"stringValue": str(value)}}


def span(trace: str, sid: str, parent: str, name: str, start_ns: int, end_ns: int, attrs: dict, error: bool = False) -> dict:
    return {"traceId": trace, "spanId": sid, "parentSpanId": parent, "name": name, "kind": 1,
            "startTimeUnixNano": str(start_ns), "endTimeUnixNano": str(max(end_ns, start_ns + 1_000_000)),
            "attributes": [_attr(k, v) for k, v in attrs.items() if v not in (None, "")],
            "status": {"code": 2 if error else 1}}


def payload(spans: list[dict]) -> dict:
    return {"resourceSpans": [{"resource": {"attributes": [_attr("service.name", SERVICE)]},
                               "scopeSpans": [{"scope": {"name": "fabryka"}, "spans": spans}]}]}


def export(spans: list[dict]) -> bool:
    if not spans:
        return True
    request = urllib.request.Request(ENDPOINT.rstrip("/") + "/v1/traces", data=json.dumps(payload(spans)).encode(),
                                     headers={"Content-Type": "application/json"})
    try:
        urllib.request.urlopen(request, timeout=3).read()
        return True
    except Exception as err:  # ślad nigdy nie zatrzymuje linii
        print(f"ślad: eksport do {ENDPOINT} nie wyszedł ({err})", file=sys.stderr)
        return False


def step_span(step: Step, start_ns: int, end_ns: int, exit_code: int) -> dict:
    return span(step.trace_id, step.span_id, step.root_id, step_name(step.node, step.run, step.attrs["fabryka.proba"]),
                start_ns, end_ns, {**step.attrs, "exit_code": exit_code}, error=exit_code != 0)


def root_span(step: Step, start_ns: int, end_ns: int, status: str) -> dict:
    return span(step.trace_id, step.root_id, "", f"zlecenie {step.attrs['fabryka.zlecenie']}", start_ns, end_ns,
                {"fabryka.run": step.run, "fabryka.zlecenie": step.attrs["fabryka.zlecenie"], "argo.status": status},
                error=status not in ("Succeeded", ""))


def _ns(ts: str) -> int:
    return int(datetime.strptime(ts, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc).timestamp() * 1e9)


def tool_spans(step: Step, events: list[dict]) -> list[dict]:
    """Zdarzenia serwera warsztatu jako spany. Odrzucone próby są błędem: widać je w śladzie na czerwono."""
    spans = []
    for n, event in enumerate(events):
        data = event.get("data", {})
        start = _ns(event["ts"])
        seconds = data.get("seconds") or 0
        rejected = event["type"] in ("gate.tamper_attempt", "holdout.peek")
        tool = data.get("tool", event["type"])
        target = data.get("path") or data.get("module") or ""
        name = f"warsztat · {tool}" + (f" {target}" if target else "") + (" ✋" if rejected else "")
        attrs = {"fabryka.event": event["type"], "mcp.tool": tool, **{f"warsztat.{k}": v for k, v in data.items()}}
        spans.append(span(step.trace_id, span_id(step.run, step.node, "narzedzie", str(n)), step.span_id, name,
                          start, start + int(seconds * 1e9), attrs, error=rejected or data.get("exit_code", 0) != 0))
    return spans


def url(trace: str | None) -> str:
    return f"{UI}/trace/{trace}" if trace else ""


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("traceparent")
    sub.add_parser("url")
    k = sub.add_parser("krok")
    k.add_argument("--start", type=int, required=True, help="początek kroku w nanosekundach (date +%%s%%N)")
    k.add_argument("--exit", type=int, default=0)
    n = sub.add_parser("narzedzia")
    n.add_argument("--events", required=True)
    r = sub.add_parser("korzen")
    r.add_argument("--start", required=True, help="{{workflow.creationTimestamp}} (RFC 3339)")
    r.add_argument("--status", default="")
    args = parser.parse_args()

    step = Step()
    if args.cmd == "traceparent":
        print(step.traceparent())
    elif args.cmd == "url":
        print(url(step.trace_id))
    elif not step.parent:
        return
    elif args.cmd == "krok":
        export([step_span(step, args.start, time.time_ns(), args.exit)])
    elif args.cmd == "korzen":
        start = int(datetime.fromisoformat(args.start.replace("Z", "+00:00")).timestamp() * 1e9)
        export([root_span(step, start, time.time_ns(), args.status)])
        print(f"ślad: {url(step.trace_id)}")
    elif args.cmd == "narzedzia":
        path = Path(args.events)
        lines = path.read_text(encoding="utf-8").splitlines() if path.exists() else []
        events = []
        for line in lines:
            try:
                events.append(json.loads(line))
            except json.JSONDecodeError:
                continue
        spans = tool_spans(step, events)
        export(spans)
        print(f"ślad: {len(spans)} wywołań narzędzi warsztatu")


if __name__ == "__main__":
    main()
