#!/usr/bin/env bash
# Wersje ilustracji do decku: 1400 px, JPEG 72. Oryginały z out/ mają po ~4 MB i zostają
# lokalnie (.gitignore); do repo i do pptx idą te lżejsze, ~0,5 MB. Slajd pokazuje
# ilustrację na 5,4 cala, więc 1400 px to i tak zapas.
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p deck
n=0
for png in out/*-v1.png; do
  [ -e "$png" ] || continue
  scena=$(basename "$png" -v1.png)
  sips -s format jpeg -s formatOptions 72 --resampleWidth 1400 "$png" --out "deck/$scena.jpg" >/dev/null
  n=$((n+1))
done
echo "zoptymalizowane: $n -> deck/*.jpg ($(du -sh deck | cut -f1))"
