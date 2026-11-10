#!/usr/bin/env bash
# Moodclock installer — works on every Linux distro
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPT="$SCRIPT_DIR/moodclock.py"
NAME="moodclock"
BIN_DIR="${XDG_BIN_HOME:-$HOME/.local/bin}"

echo ""
echo "  Moodclock installer"
echo "  ───────────────────"
echo ""

# Check Python
if ! command -v python3 >/dev/null 2>&1; then
    echo "✗ Python 3 is required but not found."
    echo "  Install it with your package manager and try again."
    exit 1
fi

# Install Python dependencies
if ! python3 -c "import rich, requests" 2>/dev/null; then
    echo "→ Installing dependencies (rich + requests)..."
    if python3 -m pip install --user --quiet rich requests 2>/dev/null; then
        echo "  ✓ Dependencies installed"
    else
        echo "  Could not install with pip --user."
        echo ""
        echo "  Try one of these:"
        echo "    pip install rich requests"
        echo "    sudo apt install python3-rich python3-requests     # Debian/Ubuntu"
        echo "    sudo dnf install python3-rich python3-requests     # Fedora"
        echo "    sudo pacman -S python-rich python-requests         # Arch"
        exit 1
    fi
else
    echo "→ Dependencies already present"
fi

# Install the command
mkdir -p "$BIN_DIR"
cp "$SCRIPT" "$BIN_DIR/$NAME"
chmod +x "$BIN_DIR/$NAME"
echo "→ Installed to $BIN_DIR/$NAME"

# Ensure ~/.local/bin is in PATH
if [[ ":$PATH:" != *":$BIN_DIR:"* ]]; then
    SHELL_RC=""
    case "${SHELL:-}" in
        *zsh*)  SHELL_RC="$HOME/.zshrc" ;;
        *bash*) SHELL_RC="$HOME/.bashrc" ;;
        *fish*) SHELL_RC="$HOME/.config/fish/config.fish" ;;
        *)      SHELL_RC="$HOME/.profile" ;;
    esac

    if [[ -n "$SHELL_RC" ]]; then
        mkdir -p "$(dirname "$SHELL_RC")"
        if [[ "$SHELL_RC" == *fish* ]]; then
            echo "fish_add_path $BIN_DIR" >> "$SHELL_RC"
        else
            echo "" >> "$SHELL_RC"
            echo "# Moodclock" >> "$SHELL_RC"
            echo "export PATH=\"\$HOME/.local/bin:\$PATH\"" >> "$SHELL_RC"
        fi
        echo "→ Added $BIN_DIR to PATH in $SHELL_RC"
        echo "  Run:  source $SHELL_RC   (or open a new terminal)"
    else
        echo "→ Warning: $BIN_DIR is not in your PATH."
        echo "  Add this line to your shell config:"
        echo "    export PATH=\"\$HOME/.local/bin:\$PATH\""
    fi
fi

echo ""
echo "✓ Done! Just type:"
echo ""
echo "    moodclock"
echo ""
echo "  Options:  moodclock -l Berlin"
echo "            moodclock -t cozy"
echo "            moodclock --list-themes"
echo ""
