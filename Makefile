
# Install the Python script as /usr/bin/kde-starship
PY_SCRIPT = src/kde_starship.py

.PHONY: install install-script install-template test clean uninstall

install: install-template install-script

install-script:
	sudo cp $(PY_SCRIPT) /usr/bin/kde-starship
	sudo chmod 755 /usr/bin/kde-starship

install-template:
	mkdir -p $(HOME)/.config/kde_starship
	cp template/starship.toml $(HOME)/.config/kde_starship/starship.toml

test:
	# Verify syntax and show --help for the Python script
	python3 -m py_compile src/kde_starship.py
	python3 src/kde_starship.py --help

clean:
	# remove compiled python cache
	rm -rf __pycache__ src/__pycache__

uninstall:
	sh ./uninstall.sh
