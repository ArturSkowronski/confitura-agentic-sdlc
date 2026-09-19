"""Minimalny klient dowolnego API zgodnego z OpenAI (LiteLLM, OpenRouter, vLLM, Ollama...).

Zmienne środowiskowe: LLM_BASE_URL, LLM_API_KEY, LLM_MODEL.
"""

from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.request


def configured() -> bool:
    return all(os.environ.get(k) for k in ("LLM_BASE_URL", "LLM_API_KEY", "LLM_MODEL"))


def chat(system: str, user: str, *, max_tokens: int = 2000, timeout: int = 180) -> str:
    body = {
        "model": os.environ["LLM_MODEL"],
        "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
        "max_tokens": max_tokens,
        "temperature": 0,
    }
    request = urllib.request.Request(
        os.environ["LLM_BASE_URL"].rstrip("/") + "/chat/completions",
        data=json.dumps(body).encode(),
        headers={"Authorization": f"Bearer {os.environ['LLM_API_KEY']}", "Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            payload = json.loads(response.read())
    except urllib.error.HTTPError as err:
        raise RuntimeError(f"LLM HTTP {err.code}: {err.read()[:300]!r}") from err
    return payload["choices"][0]["message"]["content"] or ""


def extract_json(text: str):
    """Model czasem owija JSON w ```json ... ```. Bierzemy pierwszy obiekt, który się parsuje."""
    fenced = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.S)
    candidate = fenced.group(1) if fenced else text[text.find("{"): text.rfind("}") + 1]
    return json.loads(candidate)
