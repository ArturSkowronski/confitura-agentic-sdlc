#!/usr/bin/env bash
# Przeskocz do lekcji N: make lekcja N=4. Twoje zmiany lądują w git stash, gałąź `praca` staje na tagu lekcja-04.
set -euo pipefail
cd "$(dirname "$0")/.."
N=${1:?Podaj numer lekcji, np. make lekcja N=4}
tag=$(printf 'lekcja-%02d' "$N")
git rev-parse -q --verify "refs/tags/$tag" >/dev/null || { git fetch -q --tags origin 2>/dev/null || true; }
git rev-parse -q --verify "refs/tags/$tag" >/dev/null || { echo "brak tagu $tag"; exit 1; }
if [ -n "$(git status --porcelain)" ]; then git stash push -q -u -m "przed $tag" && echo "Twoje zmiany są w: git stash list"; fi
git switch -q -C praca "$tag"
echo "praca = $tag. Materiał: warsztat/$(ls warsztat | grep "^$tag" | head -1)"
