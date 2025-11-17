# kde-starship

A small utility that generates a Starship prompt configuration from the
active KDE color scheme. This repository provides a Python script and simple
install helpers to place the command in `/usr/bin`.

Requirements
- Python 3
- `kreadconfig6` (optional but required to automatically detect the active KDE color scheme)

Install
- Using the Makefile (recommended for development):
```sh
make install
```

- Using the installer script:
```sh
sh ./install.sh
```

What gets installed
- The Python script `src/kde_starship.py` is installed as `/usr/bin/kde-starship` and marked executable.
- The default template `template/starship.toml` is copied to `$HOME/.config/kde_starship/starship.toml`.

Usage
- Generate the Starship configuration (default output):
```sh
kde-starship
```

- Specify output and template explicitly:
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

Uninstall
```sh
make uninstall
# or
sh ./uninstall.sh
```

Development and tests
- Quickly check Python syntax and view help:
```sh
make test
```

If you want the project to include a compiled binary in the future, we can add a Rust or packaged Python binary workflow, but currently this repository installs only the Python script.
