#!/usr/bin/env bash
# Akceptacja człowieka: make zatwierdz W=<przebieg> [KTO=login]. Zapisuje, kto zaakceptował, i wznawia linię.
set -euo pipefail
cd "$(dirname "$0")/.."
W=${1:?Podaj przebieg, np. make zatwierdz W=fabryka-zwroty-czesciowe-abcde (argo list -n fabryka)}
KTO=${2:-${KTO:-$(git config user.name || echo "$USER")}}
argo node set -n fabryka "$W" --output-parameter "kto=$KTO" --node-field-selector "templateName=czekaj" >/dev/null
argo resume -n fabryka "$W" >/dev/null
echo "Zaakceptowane przez: $KTO. Linia rusza dalej: argo watch -n fabryka $W"
