.PHONY: all
all: install

DEPENDENCIES = .venv/.flag

.PHONY: install
install: $(DEPENDENCIES)

$(DEPENDENCIES): poetry.lock
	@ poetry config settings.virtualenvs.in-project true
	poetry install
	@ touch $@

poetry.lock: pyproject.toml
	poetry lock
	@ touch $@

.PHONY: run
run: install
	DEBUG=true poetry run python main.py

.PHONY: format
format: install
	poetry run isort . --recursive --apply
	poetry run black .

.PHONY: check
check: install
	poetry run mypy .
