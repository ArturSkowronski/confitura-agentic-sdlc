#!/usr/bin/env bash
# make klucz: klucz do modelu dla agentów fabryki (Secret fabryka-llm + ModelConfig) i restart agentów.
# Klucz: zmienna LLM_API_KEY albo wpisany (niewidoczny) po pytaniu. Nie podawaj go jako argumentu make.
# Rodzaj klucza wybiera API: sk-ant-… to Claude API (Anthropic), sk-or-… to OpenRouter, pozostałe sk-… (sk-proj-…,
# sk-svcacct-…) to OpenAI. LLM_BASE_URL i LLM_MODEL ustawione ręcznie mają pierwszeństwo.
set -euo pipefail
cd "${FABRYKA_REPO:-$(dirname "$0")/..}"   # fabryka klucz uruchamia kopię z narzędzi, w katalogu repo
twoj_url=${LLM_BASE_URL:-}; twoj_model=${LLM_MODEL:-}
. scripts/workshop.env

k=${LLM_API_KEY:-}
if [ -z "$k" ]; then
  read -rsp "Klucz do modelu (wklej i Enter, nie będzie widoczny): " k; echo
fi
k=$(printf '%s' "$k" | tr -d '[:space:]')
[ -n "$k" ] || { echo "Pusty klucz. Nic nie zmieniam."; exit 1; }

case "$k" in
  sk-ant-*) rodzaj="Claude API (Anthropic)"; url=https://api.anthropic.com/v1; model=claude-sonnet-5 ;;
  sk-or-*)  rodzaj="OpenRouter";             url=https://openrouter.ai/api/v1;  model=anthropic/claude-sonnet-5 ;;
  sk-*)     rodzaj="OpenAI";                 url=https://api.openai.com/v1;     model=gpt-5.4 ;;
  *)        rodzaj="API zgodne z OpenAI";    url=$LLM_BASE_URL;                 model=$LLM_MODEL ;;
esac
LLM_BASE_URL=${twoj_url:-$url}; LLM_MODEL=${twoj_model:-$model}
echo "Klucz ${k:0:10}… → $rodzaj, $LLM_BASE_URL, model $LLM_MODEL"

# Jedno krótkie zapytanie, zanim klucz trafi do klastra: zły klucz albo model widać tu, a nie w logach agenta.
if [ "${KLUCZ_BEZ_TESTU:-0}" != 1 ]; then
  LLM_API_KEY="$k" LLM_BASE_URL="$LLM_BASE_URL" LLM_MODEL="$LLM_MODEL" python3 - <<'PY' || { echo "Klucz nie zapisany. Wymuszenie bez testu: KLUCZ_BEZ_TESTU=1 fabryka klucz"; exit 1; }
import json, os, sys, urllib.request, urllib.error
def zapytaj(limit):
    # Modele OpenAI z rodziny gpt-5 i o-series odrzucają max_tokens (HTTP 400), chcą max_completion_tokens.
    req = urllib.request.Request(os.environ["LLM_BASE_URL"].rstrip("/") + "/chat/completions",
        data=json.dumps({"model": os.environ["LLM_MODEL"], limit: 20,
                         "messages": [{"role": "user", "content": "Odpowiedz: ok"}]}).encode(),
        headers={"Authorization": "Bearer " + os.environ["LLM_API_KEY"], "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        json.load(r)
try:
    try:
        zapytaj("max_tokens")
    except urllib.error.HTTPError as e:
        e.tresc = e.read()   # odczyt zużywa ciało odpowiedzi: zachowujemy je dla komunikatu niżej
        if e.code != 400 or b"max_completion_tokens" not in e.tresc:
            raise
        zapytaj("max_completion_tokens")
    print("Test modelu: odpowiada.")
except urllib.error.HTTPError as e:
    body = getattr(e, "tresc", None) or e.read()
    body = body[:300].decode(errors="replace")
    powod = {401: "klucz odrzucony (zły albo unieważniony)", 403: "brak dostępu do tego modelu",
             404: "nieznany model albo adres API", 429: "limit albo brak kredytu na koncie"}.get(e.code, "błąd API")
    print(f"Test modelu: HTTP {e.code}, {powod}.\n  {body}"); sys.exit(1)
except Exception as e:
    print(f"Test modelu: brak połączenia z {os.environ['LLM_BASE_URL']}: {e}"); sys.exit(1)
PY
fi

kubectl create secret generic fabryka-llm -n fabryka --from-literal=LLM_API_KEY="$k" --dry-run=client -o yaml | kubectl apply -f - >/dev/null
LLM_MODEL="$LLM_MODEL" LLM_BASE_URL="$LLM_BASE_URL" envsubst < platforma/kagent/modelconfig.yaml | kubectl apply -f - >/dev/null
kubectl rollout restart deploy -n fabryka -l app=kagent >/dev/null 2>&1 || true
echo "Zapisane. Agenci wstają z nowym kluczem (około minuty). Sprawdzenie: make a2a A=probny T=\"Przedstaw się\""
