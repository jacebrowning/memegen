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
	rm -rf images templates-legacy templates/_custom-* tests/images
	rm -rf *.egg-info .venv

###############################################################################
# Development Tasks

PACKAGES := app scripts

.PHONY: run
run: install
	DEBUG=true poetry run python app/views.py

.PHONY: format
format: install
	poetry run autoflake --recursive $(PACKAGES) --in-place --remove-all-unused-imports
	poetry run isort $(PACKAGES) --recursive --apply
	poetry run black $(PACKAGES)

.PHONY: check
check: install
	poetry run mypy $(PACKAGES)

.PHONY: test
test: install
	@ if test -e .cache/v/cache/lastfailed; then \
		echo "Running failed tests..." && \
		poetry run pytest --last-failed --maxfail=1 --no-cov && \
		echo "Running all tests..." && \
		poetry run pytest --cache-clear; \
	else \
		echo "Running all tests..." && \
		poetry run pytest --new-first --maxfail=1; \
	fi
	poetry run coveragespace jacebrowning/memegen-v2 overall

.PHONY: watch
watch: install
	@ sleep 2 && touch */__init__.py &
	@ poetry run watchmedo shell-command --recursive --pattern="*.py;*.yml" --command="clear && make test check format && echo && echo ✅ && echo" --wait --drop

###############################################################################
# Delivery Tasks

.PHONY: import
import: install
	poetry run gitman update --force --quiet
	poetry run python scripts/import_legacy_templates.py

.PHONY: promote
promote: install
	SITE=https://memegen-link-v2-staging.herokuapp.com poetry run pytest scripts --verbose --no-cov
	heroku pipelines:promote --app memegen-link-v2-staging --to memegen-link-v2
	SITE=https://memegen-link-v2.herokuapp.com poetry run pytest scripts --verbose --no-cov
