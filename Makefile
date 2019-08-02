PACKAGES := backend tests

.PHONY: all
all: install

.PHONY: ci
ci: test format check

###############################################################################
# Project Dependencies

DEPENDENCIES := .venv/.flag

.PHONY: install
install: $(DEPENDENCIES)

$(DEPENDENCIES): poetry.lock
	@ poetry config settings.virtualenvs.in-project true
	poetry install
	poetry run pip freeze > requirements.txt
	grep -v memegen requirements.txt > requirements.txt.tmp
	mv requirements.txt.tmp requirements.txt
	@ touch $@

poetry.lock: pyproject.toml
	poetry lock
	@ touch $@

###############################################################################
# Development Tasks

.PHONY: run
run: install
	DEBUG=true poetry run python backend/main.py

.PHONY: format
format: install
	poetry run isort $(PACKAGES) --recursive --apply
	poetry run black $(PACKAGES)

.PHONY: check
check: install
	poetry run mypy $(PACKAGES)

.PHONY: test
test: install
	poetry run pytest --cov=backend --cov-branch

.PHONY: coverage
coverage: install
	poetry run coveragespace jacebrowning/memegen-v2 overall

.PHONY: watch
watch: install
	poetry run pytest-watch --nobeep --runner="make test" --onpass="make coverage format check && clear"

###############################################################################
# Production Tasks

.PHONY: run-production
run-production: install
	PORT=8000 poetry run heroku local
