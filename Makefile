PACKAGES := server tests

.PHONY: all
all: install

###############################################################################
# Project Dependencies

DEPENDENCIES := .venv/.flag

.PHONY: install
install: $(DEPENDENCIES)

$(DEPENDENCIES): poetry.lock
	@ poetry config settings.virtualenvs.in-project true
	poetry install
	@ touch $@

poetry.lock: pyproject.toml
	poetry lock
	@ touch $@

###############################################################################
# Development Tasks

.PHONY: run
run: install
	DEBUG=true poetry run python server/main.py

.PHONY: format
format: install
	poetry run isort $(PACKAGES) --recursive --apply
	poetry run black $(PACKAGES)

.PHONY: check
check: install
	poetry run mypy $(PACKAGES)

.PHONY: test
test: install
	poetry run pytest
