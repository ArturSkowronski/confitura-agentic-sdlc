#!/usr/bin/env bash
# Lekcje to łańcuch commitów na main z tagami lekcja-01 … lekcja-10 (main = lekcja-10).
# Poprawkę wspólną dla wszystkich lekcji zrób na commicie lekcji, w której powstała (np. git rebase -i lekcja-03~1),
# a potem przestaw tagi na nowe commity:  scripts/restack.sh [--push]
# Skrypt szuka commitów po tytule „Lekcja N:” w historii main.
set -euo pipefail
cd "$(dirname "$0")/.."
log=$(git log main --format='%H %s')
tags=()
for n in $(seq 1 10); do
  tag=$(printf 'lekcja-%02d' "$n")
  sha=$(printf '%s\n' "$log" | grep -m1 " Lekcja $n: " | cut -d' ' -f1 || true)
  if [ -z "$sha" ]; then echo "  (brak commitu „Lekcja $n:” na main, pomijam $tag)"; continue; fi
  git tag -f "$tag" "$sha" >/dev/null
  tags+=("$tag")
done
git log --oneline --decorate main | grep -E 'tag: lekcja-' | head -12
if [ "${1:-}" = "--push" ]; then
  git push -f origin main "${tags[@]}"
fi
