#!/usr/bin/env bash
# Natywny .key z .pptx, przez samego Keynote'a. pptxgenjs nie umie pisać formatu Apple,
# więc konwersję robi aplikacja: otwiera pptx, zapisuje jako .key, zamyka.
#
# Uwaga: aplikacja bywa przemianowana na dysku (u Artura "Keynote Creator Studio.app"),
# dlatego adresujemy ją identyfikatorem pakietu, a nie nazwą.
set -euo pipefail
cd "$(dirname "$0")"
SRC="$PWD/fabryka-od-podstaw.pptx"
DST="$PWD/fabryka-od-podstaw.key"
[ -f "$SRC" ] || { echo "brak $SRC — najpierw node build.mjs"; exit 1; }
osascript <<OSA >/dev/null
tell application id "com.apple.Keynote"
  set d to open POSIX file "$SRC"
  delay 3
  save d in POSIX file "$DST"
  delay 2
  close d saving no
end tell
OSA
echo "zapisane: $(basename "$DST") ($(/usr/bin/du -h "$DST" | cut -f1))"
