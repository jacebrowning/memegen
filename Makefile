.PHONY: all
all: install

.PHONY: ci
ci: format check test

###############################################################################
# System Dependencies

.PHONY: doctor
doctor:
	bin/verchew --exit-code

###############################################################################
# Project Dependencies

BACKEND_DEPENDENCIES := .venv/.flag

.PHONY: install
install: $(BACKEND_DEPENDENCIES)

$(BACKEND_DEPENDENCIES): poetry.lock runtime.txt requirements.txt
	@ poetry config virtualenvs.in-project true
	poetry install
	@ touch $@

ifndef CI
poetry.lock: pyproject.toml
	poetry lock
	@ touch $@
runtime.txt: .python-version
	echo "python-$(shell cat $<)" > $@
requirements.txt: poetry.lock
	poetry export --format requirements.txt --output $@ --without-hashes
endif

.PHONY: clean
clean:
	rm -rf .venv

###############################################################################
# Development Tasks

.PHONY: run
run: install
	DEBUG=true poetry run heroku local

.PHONY: format
format: install
	poetry run autoflake --recursive app --in-place --remove-all-unused-imports
	poetry run isort app --recursive --apply
	poetry run black app

.PHONY: check
check: install
	poetry run mypy app

.PHONY: test
test: install
	cd app && poetry run pytest --cov=app --cov-branch --disable-warnings
	cd app && poetry run coveragespace jacebrowning/memegen-v2 overall

.PHONY: watch
watch: install
	poetry run pytest-watch --runner="make test" --onpass="make check format && clear && echo 'All tests passed.'" --nobeep --wait

###############################################################################
# Migration Tasks

.PHONY: import
import: install
	poetry run gitman update --force --quiet
	poetry run python app/import_legacy_templates.py
