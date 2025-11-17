# kde-starship

A small utility that generates a Starship configuration from the
active KDE color scheme. This repository provides a Python script and simple
install helpers to place the command in `/usr/bin`.

Requirements
- Python 3
- `kreadconfig6` (required to automatically detect the active KDE color scheme)

Install

- Using the installer script:
```sh
chmod +x install.sh
sudo sh ./install.sh
```

Uninstall
- Using the installer script:
```sh
chmod +x install.sh
sudo sh ./uninstall.sh
```

What gets installed
- The Python script `src/kde_starship.py` is installed as `/usr/bin/kde-starship` and marked executable.
- My custom default template `template/starship.toml` is copied to `$HOME/.config/kde_starship/starship.toml`.

Usage
- Generate the Starship configuration (default output `$HOME/.config/starship.toml`):
```sh
kde-starship -t /path/to/template/starship.toml
```
or specific output
```sh
kde-starship -o ~/.config/starship.toml -t /path/to/template/starship.toml
```

- Show help:
```sh
kde-starship --help
```

Notes
- Installing to `/usr/bin` requires `sudo`.
- The installer will not overwrite an existing user template unexpectedly; the uninstall script only removes the installed template if it matches the repository template.
