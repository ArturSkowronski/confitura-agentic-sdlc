#!/usr/bin/env bash
# Para kluczy fabryki do podpisywania księgi (Sigstore cosign, klucz offline: sala bez Wi-Fi nie zablokuje lekcji).
# Klucz prywatny trafia do Secretu w klastrze (krok `ksiega` linii), publiczny zostaje w repo do weryfikacji.
set -euo pipefail
cd "$(dirname "$0")/.."
dir=platforma/linia/cosign
mkdir -p "$dir"
if [ ! -f "$dir/cosign.key" ]; then
  (cd "$dir" && COSIGN_PASSWORD="" cosign generate-key-pair >/dev/null 2>&1)
  echo "nowa para kluczy: $dir/cosign.key (prywatny, poza gitem) i $dir/cosign.pub"
fi
kubectl create secret generic fabryka-cosign -n fabryka --from-file=cosign.key="$dir/cosign.key" \
  --from-literal=COSIGN_PASSWORD="" --dry-run=client -o yaml | kubectl apply -f - >/dev/null
echo "Secret fabryka-cosign gotowy. Weryfikacja: cosign verify-blob --key $dir/cosign.pub --bundle <plik>.sigstore.json <plik>"
