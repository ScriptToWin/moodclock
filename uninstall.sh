#!/usr/bin/env bash
# mdc uninstaller

NAME="mdc"
BIN_DIR="${XDG_BIN_HOME:-$HOME/.local/bin}"
TARGET="$BIN_DIR/$NAME"

if [ -f "$TARGET" ]; then
    rm -f "$TARGET"
    echo "  ✓ Removed executable from $TARGET"
else
    echo "  - Executable not found at $TARGET"
fi

SHELL_RC=""
case "${SHELL:-}" in
    *zsh*)  SHELL_RC="$HOME/.zshrc" ;;
    *bash*) SHELL_RC="$HOME/.bashrc" ;;
    *fish*) SHELL_RC="$HOME/.config/fish/config.fish" ;;
    *)      SHELL_RC="$HOME/.profile" ;;
esac

if [[ -n "$SHELL_RC" && -f "$SHELL_RC" ]]; then
    if grep -q "# mdc" "$SHELL_RC"; then
        sed -i.bak '/# mdc/,+1d' "$SHELL_RC"
        echo "  ✓ Removed PATH entry from $SHELL_RC"
    fi
fi

echo "✓ Uninstallation complete!"
