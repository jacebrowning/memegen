.PHONY: all
all: install

DEPENDENCIES = .venv/.flag

.PHONY: install
install: $(DEPENDENCIES) requirements.txt

$(DEPENDENCIES): poetry.lock
	@ poetry config settings.virtualenvs.in-project true
	poetry install
	@ touch $@

poetry.lock: pyproject.toml
	poetry lock
	@ touch $@

requirements.txt: poetry.lock
	@ echo "# Exported dependencies for Heroku" > $@
	@ poetry run pip freeze >> $@ 2> /dev/null

.PHONY: run
run: install
	DEBUG=true poetry run python main.py

.PHONY: format
format: install
	poetry run isort . --recursive --apply
	poetry run black .

