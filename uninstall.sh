#!/usr/bin/env sh
set -e

PKG_PY="/usr/bin/kde-starship"
REPO_TEMPLATE="template/starship.toml"
INST_TEMPLATE="$HOME/.config/kde_starship/starship.toml"

echo "Uninstalling installed files (sudo required)..."
sudo rm -f "$PKG_PY" || true

if [ -f "$INST_TEMPLATE" ] && [ -f "$REPO_TEMPLATE" ]; then
  if cmp -s "$INST_TEMPLATE" "$REPO_TEMPLATE"; then
    echo "Installed template matches the repository template; removing $INST_TEMPLATE"
    rm -f "$INST_TEMPLATE"
  else
    echo "Installed template $INST_TEMPLATE differs from repository template; leaving it in place."
  fi
fi

echo "Uninstall complete."
