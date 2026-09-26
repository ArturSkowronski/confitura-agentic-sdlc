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
sudo apt-get update -qq && sudo apt-get install -y -qq jq gettext-base python3 >/dev/null   # python3: fabryka i sdlc/ (tylko biblioteka standardowa)
rm -rf "$tmp"
git config --global --add safe.directory '*'   # workspace montowany z innym właścicielem
bash warsztat/narzedzia/instaluj.sh
sudo ln -sf "$HOME/.local/bin/fabryka" /usr/local/bin/fabryka   # widoczne też w powłokach bez .bashrc (gh codespace ssh -- ...)
# Claude Code natywnym instalatorem (jeden plik, bez Node). Feature devcontainera instalował go przez npm na Node 18,
# czyli w starej wersji. Błąd sieci nie zatrzymuje codespace'a: fabryka autopilot powie, jak doinstalować.
if curl -fsSL https://claude.ai/install.sh | bash >/dev/null 2>&1; then
  sudo ln -sf "$HOME/.local/bin/claude" /usr/local/bin/claude
  echo "Claude Code $(claude --version 2>/dev/null | cut -d' ' -f1). Logowanie: fabryka zaloguj"
else
  echo "Uwaga: Claude Code się nie zainstalował. Później: curl -fsSL https://claude.ai/install.sh | bash"
fi
echo "Narzędzia gotowe: kind $(kind version | cut -d' ' -f2), argo $ARGO_VERSION, cosign $COSIGN_VERSION, fabryka."
