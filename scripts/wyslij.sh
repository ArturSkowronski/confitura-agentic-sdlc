#!/usr/bin/env bash
# Wkłada snapshot Twojego repo do klastra: /work/repo w magazynie. Idzie cała historia gita (z niej liczymy
# faktycznych właścicieli modułów, L3) i Twój working tree, zapisany jako commit na main Twoim nazwiskiem.
# Zero serwera git, zero tokenów. Linia i agent pracują na tej kopii, wynik wraca przez make odbierz.
set -euo pipefail
cd "$(dirname "$0")/.."
pod=$(kubectl get pod -n fabryka -l app=magazyn -o jsonpath='{.items[0].metadata.name}' 2>/dev/null)
[ -n "$pod" ] || { echo "brak magazynu: make setup"; exit 1; }
who=$(git config user.name || echo "uczestnik"); mail=$(git config user.email || echo "uczestnik@warsztat")
COPYFILE_DISABLE=1 tar --no-xattrs --exclude target --exclude .sdlc --exclude __pycache__ --exclude .jqwik-database \
  -czf - . 2>/dev/null | kubectl exec -i -n fabryka "$pod" -- sh -c "
  rm -rf /work/repo && mkdir -p /work/repo /work/out && tar -xzf - -C /work/repo && cd /work/repo \
  && git config user.name '$who' && git config user.email '$mail' \
  && git switch -q -C main && git add -A \
  && (git commit -qm 'snapshot: working tree z laptopa' >/dev/null 2>&1 || true) \
  && git log --oneline -1"
