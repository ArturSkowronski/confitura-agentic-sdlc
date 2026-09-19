#!/usr/bin/env bash
# Wyślij zlecenie na linię: snapshot repo do klastra, potem Argo Workflow z szablonu `fabryka`.
#   scripts/zlecenie.sh rabat [kagent|replay] [proba]
set -euo pipefail
cd "$(dirname "$0")/.."
Z=${1:?Podaj zlecenie, np. make zlecenie Z=rabat}
AGENT=${2:-${AGENT:-kagent}}
PROBA=${3:-1}
[ -f "zlecenia/$Z.md" ] || { echo "brak zlecenia zlecenia/$Z.md"; ls zlecenia; exit 1; }
scripts/wyslij.sh >/dev/null
name=$(argo submit -n fabryka --from workflowtemplate/fabryka -p "zlecenie=$Z" -p "agent=$AGENT" -p "proba=$PROBA" -p "modul=${REPLAY_MODULE:-}" \
  --generate-name "fabryka-$Z-" -o name)
echo "Przebieg: $name (agent=$AGENT, próba $PROBA). Hala: http://localhost:2746/workflows/fabryka/$name"
argo watch -n fabryka "$name" 2>/dev/null | tail -n 25 || true
status=$(argo get -n fabryka "$name" -o json | jq -r .status.phase)
echo "Wynik: $status. Odbierz: make odbierz"
[ "$status" = "Succeeded" ]
