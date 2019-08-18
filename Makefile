PACKAGES := backend tests

.PHONY: all
all: install

.PHONY: ci
ci: test format check

###############################################################################
# System Dependencies

.PHONY: doctor
doctor:
	bin/verchew --exit-code

.envrc: Makefile
	echo > $@
	echo export FRONTEND_PORT=5000 >> $@
	echo export BACKEND_PORT=5001 >> $@
	echo export REACT_APP_BACKEND_URL=http://localhost:5001 >> $@
	echo >> $@
	echo export BROWSER=firefox >> $@
	direnv allow

###############################################################################
# Project Dependencies

BACKEND_DEPENDENCIES := .venv/.flag
FRONTEND_DEPENDENCIES := frontend/node_modules/.flag

.PHONY: install
install: $(BACKEND_DEPENDENCIES) $(FRONTEND_DEPENDENCIES)

$(BACKEND_DEPENDENCIES): poetry.lock
	@ poetry config settings.virtualenvs.in-project true
	poetry install
	@ poetry run pip freeze > requirements.txt
	@ grep -v memegen requirements.txt > requirements.txt.tmp
	@ mv requirements.txt.tmp requirements.txt
	@ touch $@

$(FRONTEND_DEPENDENCIES): frontend/yarn.lock
	cd frontend && yarn install
	@ touch $@

ifndef CI
poetry.lock: pyproject.toml
	poetry lock
	@ touch $@
endif

###############################################################################
# Development Tasks

.PHONY: run
run: install
	poetry run honcho start --procfile Procfile.dev

.PHONY: format
format: install
	poetry run isort $(PACKAGES) --recursive --apply
	poetry run black $(PACKAGES)

.PHONY: check
check: install
	poetry run mypy $(PACKAGES)

.PHONY: test
test: install
	BACKEND_PORT=1234 poetry run pytest tests --cov=backend --cov-branch
	cd frontend && CI=true yarn test

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
	unset REACT_APP_BACKEND_URL && cd frontend && yarn build
	poetry run heroku local
