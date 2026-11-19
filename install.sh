#!/usr/bin/env bash
# mdc installer
set -eu

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPT="$SCRIPT_DIR/moodclock.py"
NAME="mdc"
BIN_DIR="${XDG_BIN_HOME:-$HOME/.local/bin}"

echo ""
echo "  mdc Installer"
echo "  ─────────────────────────────"
echo ""

if ! command -v python3 >/dev/null 2>&1; then
    echo "✗ Python 3 is required."
    exit 1
fi

if ! python3 -c "import rich, requests" 2>/dev/null; then
    echo "→ Installing dependencies (rich + requests)..."
    python3 -m pip install --user --quiet rich requests
fi

mkdir -p "$BIN_DIR"
cp "$SCRIPT" "$BIN_DIR/$NAME"
chmod +x "$BIN_DIR/$NAME"
echo "→ Installed to $BIN_DIR/$NAME"

if [[ ":$PATH:" != *":$BIN_DIR:"* ]]; then
    SHELL_RC=""
    case "${SHELL:-}" in
        *zsh*)  SHELL_RC="$HOME/.zshrc" ;;
        *bash*) SHELL_RC="$HOME/.bashrc" ;;
        *fish*) SHELL_RC="$HOME/.config/fish/config.fish" ;;
        *)      SHELL_RC="$HOME/.profile" ;;
    end

    if [[ -n "$SHELL_RC" ]]; then
        mkdir -p "$(dirname "$SHELL_RC")"
        if [[ "$SHELL_RC" == *fish* ]]; then
            echo "fish_add_path $BIN_DIR" >> "$SHELL_RC"
        else
            echo "" >> "$SHELL_RC"
            echo "# mdc" >> "$SHELL_RC"
            echo "export PATH=\"\$HOME/.local/bin:\$PATH\"" >> "$SHELL_RC"
        fi
        echo "→ Added $BIN_DIR to PATH in $SHELL_RC"
    fi
fi

echo ""
echo "✓ Done! Just type: mdc"
echo ""
