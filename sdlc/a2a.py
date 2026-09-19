"""Klient A2A (Agent2Agent, Linux Foundation) dla agentów kagent. Tylko biblioteka standardowa.

kagent wystawia każdego agenta pod /api/a2a/<namespace>/<agent>/ (JSON-RPC, A2A 0.3).
Wołamy `message/send` i zwracamy tekst ostatniego artefaktu albo ostatniej wiadomości agenta.

Zmienne środowiskowe:
  KAGENT_URL     domyślnie http://localhost:8083 (lokalnie: make port-forward),
                 w klastrze http://kagent-controller.kagent.svc:8083
  KAGENT_NS      domyślnie fabryka (namespace agentów fabryki; platforma kagent siedzi w kagent)
  A2A_USER       nagłówek X-User-Id (kagent nie uwierzytelnia, ale zapisuje, kto pytał)

Użycie:
  python3 sdlc/a2a.py --agent probny --task "Przedstaw się"
  python3 sdlc/a2a.py --agent wykonawca --file .sdlc/prompt.md
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
import uuid


def base_url() -> str:
    return os.environ.get("KAGENT_URL", "http://localhost:8083").rstrip("/")


def agent_url(agent: str, namespace: str | None = None) -> str:
    ns = namespace or os.environ.get("KAGENT_NS", "fabryka")
    return f"{base_url()}/api/a2a/{ns}/{agent}/"  # ukośnik na końcu jest obowiązkowy


def card(agent: str, namespace: str | None = None, timeout: int = 10) -> dict:
    with urllib.request.urlopen(agent_url(agent, namespace) + ".well-known/agent-card.json", timeout=timeout) as r:
        return json.loads(r.read())


def send(agent: str, text: str, *, namespace: str | None = None, session: str | None = None,
         timeout: int = 600) -> str:
    """Jedno pytanie, jedna odpowiedź. `session` (contextId) pozwala kontynuować rozmowę."""
    message = {"kind": "message", "role": "user", "messageId": str(uuid.uuid4()),
               "parts": [{"kind": "text", "text": text}]}
    if session:
        message["contextId"] = session
    body = {"jsonrpc": "2.0", "id": str(uuid.uuid4()), "method": "message/send", "params": {"message": message}}
    request = urllib.request.Request(
        agent_url(agent, namespace), data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json", "X-User-Id": os.environ.get("A2A_USER", "fabryka@warsztat")})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            payload = json.loads(response.read())
    except urllib.error.HTTPError as err:
        raise RuntimeError(f"A2A HTTP {err.code} dla agenta {agent}: {err.read()[:300]!r}") from err
    except urllib.error.URLError as err:
        raise RuntimeError(f"A2A: brak połączenia z {base_url()} ({err.reason}). Uruchom: make port-forward") from err
    if "error" in payload:
        raise RuntimeError(f"A2A błąd od agenta {agent}: {payload['error']}")
    return extract_text(payload["result"])


def extract_text(result: dict) -> str:
    """Task A2A: najpierw artefakty, potem ostatnia wiadomość agenta w historii."""
    if result.get("kind") == "message":
        return _parts(result.get("parts", []))
    artifacts = result.get("artifacts") or []
    texts = [_parts(a.get("parts", [])) for a in artifacts]
    texts = [t for t in texts if t]
    if texts:
        return "\n".join(texts)
    for message in reversed(result.get("history") or []):
        if message.get("role") == "agent":
            text = _parts(message.get("parts", []))
            if text:
                return text
    state = (result.get("status") or {}).get("state", "?")
    raise RuntimeError(f"A2A: agent nie zwrócił tekstu (stan zadania: {state})")


def _parts(parts: list[dict]) -> str:
    return "\n".join(p.get("text", "") for p in parts if p.get("kind") == "text").strip()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--agent", required=True)
    parser.add_argument("--task")
    parser.add_argument("--file", help="plik z treścią zadania")
    parser.add_argument("--session")
    parser.add_argument("--card", action="store_true", help="tylko pokaż kartę agenta")
    args = parser.parse_args()
    if args.card:
        print(json.dumps(card(args.agent), ensure_ascii=False, indent=2))
        return
    text = open(args.file, encoding="utf-8").read() if args.file else args.task
    if not text:
        parser.error("podaj --task albo --file")
    print(send(args.agent, text, session=args.session))


if __name__ == "__main__":
    main()
