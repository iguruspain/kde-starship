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

# Determine target user home directory. If script is run with sudo,
# prefer the original user's home directory (from SUDO_USER). Otherwise use $HOME.
if [ -n "$SUDO_USER" ]; then
  # Use getent to find the home directory for the original user; fallback to HOME
  USER_HOME=$(getent passwd "$SUDO_USER" | cut -d: -f6 || true)
  if [ -z "$USER_HOME" ]; then
    USER_HOME="$HOME"
  fi
else
  USER_HOME="$HOME"
fi

CONFIG_DIR="$USER_HOME/.config/kde_starship"
mkdir -p "$CONFIG_DIR"
if [ -f "template/starship.toml" ]; then
  cp "template/starship.toml" "$CONFIG_DIR/starship.toml"
  # If we created/copied as root (sudo), make sure the file is owned by the user.
  if [ -n "$SUDO_USER" ]; then
    chown -R "$SUDO_USER":"$SUDO_USER" "$CONFIG_DIR" || true
  fi
  echo "Template installed to $CONFIG_DIR/starship.toml"
else
  echo "Warning: template/starship.toml not found in repository." >&2
fi

echo "Installation complete — Python script installed as /usr/bin/kde-starship."
