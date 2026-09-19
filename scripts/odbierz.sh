#!/usr/bin/env bash
# Odbiera wyniki linii z klastra (/work/out) do .sdlc/out/<zlecenie>/proba-N/: łatka, opis, raporty, księga.
set -euo pipefail
cd "$(dirname "$0")/.."
pod=$(kubectl get pod -n fabryka -l app=magazyn -o jsonpath='{.items[0].metadata.name}')
mkdir -p .sdlc/out
kubectl exec -n fabryka "$pod" -- tar -czf - -C /work out 2>/dev/null | tar -xzf - -C .sdlc
echo "Wyniki w .sdlc/out/:"; find .sdlc/out -type f | sort | sed 's/^/  /'
