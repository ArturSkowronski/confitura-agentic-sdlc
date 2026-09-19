#!/usr/bin/env bash
# Wkłada snapshot Twojego repo (working tree, bez .git i target) do klastra: /work/repo w magazynie.
# Zero serwera git, zero tokenów. Linia i agent pracują na tej kopii, wynik wraca przez make odbierz.
set -euo pipefail
cd "$(dirname "$0")/.."
pod=$(kubectl get pod -n fabryka -l app=magazyn -o jsonpath='{.items[0].metadata.name}' 2>/dev/null)
[ -n "$pod" ] || { echo "brak magazynu: make klaster"; exit 1; }
COPYFILE_DISABLE=1 tar --no-xattrs --exclude .git --exclude target --exclude .sdlc --exclude __pycache__ \
  --exclude .jqwik-database -czf - . 2>/dev/null | kubectl exec -i -n fabryka "$pod" -- sh -c '
  rm -rf /work/repo && mkdir -p /work/repo /work/out && tar -xzf - -C /work/repo && cd /work/repo \
  && git init -q -b main && git add -A \
  && git -c user.name=fabryka -c user.email=fabryka@warsztat commit -qm "snapshot $(date -u +%FT%TZ)" \
  && git log --oneline -1'
