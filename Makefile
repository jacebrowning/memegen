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
	poetry run pytest --cov=server --cov-branch

.PHONY: coverage
coverage: install
	poetry run coveragespace jacebrowning/memegen-v2 overall --exit-code

.PHONY: watch
watch: install
	poetry run pytest-watch --nobeep --runner="make test" --onpass="make coverage format check && clear"
