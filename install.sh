#!/usr/bin/env sh
# Simple installer script: install the Python script into /usr/bin

set -e

PY_SCRIPT="src/kde_starship.py"

echo "Installing files (sudo required to copy to /usr/bin)..."

echo "Installing Python script to /usr/bin/kde-starship..."
if [ -f "$PY_SCRIPT" ]; then
  sudo cp "$PY_SCRIPT" /usr/bin/kde-starship
  sudo chmod 755 /usr/bin/kde-starship
else
  echo "Error: $PY_SCRIPT not found in the repository." >&2
  exit 1
fi

# Install the template into $HOME/.config/kde_starship/starship.toml if present
CONFIG_DIR="$HOME/.config/kde_starship"
mkdir -p "$CONFIG_DIR"
if [ -f "template/starship.toml" ]; then
  cp "template/starship.toml" "$CONFIG_DIR/starship.toml"
  echo "Template installed to $CONFIG_DIR/starship.toml"
else
  echo "Warning: template/starship.toml not found in repository." >&2
fi

echo "Installation complete — Python script installed as /usr/bin/kde-starship."
