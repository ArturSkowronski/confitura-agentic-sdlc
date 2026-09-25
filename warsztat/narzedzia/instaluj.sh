#!/usr/bin/env bash
# Instaluje narzędzia uczestnika poza repo, żeby przełączanie lekcji ich nie usuwało:
#   ~/.local/bin/fabryka                        CLI (fabryka lekcja|mapa|sprawdz|rozwiazanie|autopilot)
#   ~/.local/share/fabryka/autopilot/*.md       prompty autopilota, po jednym na lekcję
#   ~/.claude/commands/fabryka-autopilot.md     komenda Claude Code: /fabryka-autopilot N
set -euo pipefail
src=$(cd "$(dirname "$0")" && pwd)
bin=${FABRYKA_BIN:-$HOME/.local/bin}
data=${FABRYKA_DATA:-$HOME/.local/share/fabryka}
mkdir -p "$bin" "$data/autopilot" "$HOME/.claude/commands"
install -m 0755 "$src/fabryka" "$bin/fabryka"
cp "$src"/autopilot/*.md "$data/autopilot/"
cp "$src/claude-autopilot.md" "$HOME/.claude/commands/fabryka-autopilot.md"
case ":$PATH:" in
  *":$bin:"*) ;;
  *) for rc in "$HOME/.bashrc" "$HOME/.zshrc"; do
       [ -f "$rc" ] && ! grep -q 'fabryka: PATH' "$rc" && printf '\nexport PATH="%s:$PATH"  # fabryka: PATH\n' "$bin" >> "$rc"
     done
     echo "Dodałem $bin do PATH w ~/.bashrc i ~/.zshrc. Otwórz nowy terminal albo: export PATH=\"$bin:\$PATH\"" ;;
esac
echo "Zainstalowane: fabryka ($bin), $(ls "$data/autopilot" | wc -l | tr -d ' ') promptów autopilota, komenda /fabryka-autopilot w Claude Code."
