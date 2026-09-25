#!/usr/bin/env bash
# Narzędzia, których nie dają features devcontainera: kind, argo, cosign (te same wersje co u prowadzącego),
# plus narzędzia warsztatu (fabryka, prompty autopilota, /fabryka-autopilot w Claude Code).
set -euo pipefail
arch=$(dpkg --print-architecture)
KIND_VERSION=v0.33.0
ARGO_VERSION=v4.1.4
COSIGN_VERSION=v3.1.3
tmp=$(mktemp -d)
curl -fsSL -o "$tmp/kind" "https://kind.sigs.k8s.io/dl/$KIND_VERSION/kind-linux-$arch"
curl -fsSL "https://github.com/argoproj/argo-workflows/releases/download/$ARGO_VERSION/argo-linux-$arch.gz" | gunzip > "$tmp/argo"
curl -fsSL -o "$tmp/cosign" "https://github.com/sigstore/cosign/releases/download/$COSIGN_VERSION/cosign-linux-$arch"
sudo install -m 0755 "$tmp/kind" "$tmp/argo" "$tmp/cosign" /usr/local/bin/
sudo apt-get update -qq && sudo apt-get install -y -qq jq gettext-base >/dev/null
rm -rf "$tmp"
bash warsztat/narzedzia/instaluj.sh
echo "Narzędzia gotowe: kind $(kind version | cut -d' ' -f2), argo $ARGO_VERSION, cosign $COSIGN_VERSION, fabryka."
