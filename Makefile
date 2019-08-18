.PHONY: all
all: install

.PHONY: ci
ci: format check test

###############################################################################
# System Dependencies

.PHONY: doctor
doctor:
	bin/verchew --exit-code

.envrc: Makefile
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

.PHONY: clean
clean:
	rm -rf .venv
	rm -rf frontend/build
	rm -rf frontend/node_modules

###############################################################################
# Development Tasks

.PHONY: run
run: install
	poetry run honcho start --procfile Procfile.dev

.PHONY: format
format: format-backend

.PHONY: check
check: check-backend

.PHONY: test
test: test-backend test-frontend test-system

.PHONY: test-system
test-system: install
ifdef CYPRESS_SITE
	cd frontend && yarn run cypress run
else
	poetry run honcho start --procfile Procfile.e2e
endif

# Backend

.PHONY: format-backend
format-backend: install
	poetry run isort backend --recursive --apply
	poetry run black backend

.PHONY: check-backend
check-backend: install
	poetry run mypy backend

.PHONY: test-backend
test-backend: install
	cd backend && poetry run pytest --cov=backend --cov-branch

.PHONY: coverage
coverage: install
	poetry run coveragespace jacebrowning/memegen-v2 overall

.PHONY: watch
watch: install
	poetry run pytest-watch --nobeep --runner="make test" --onpass="make coverage format check && clear"

# Frontend

.PHONY: test-frontend
test-frontend: install
	cd frontend && CI=true yarn test

###############################################################################
# Production Tasks

.PHONY: run-production
run-production: install build
	poetry run heroku local

.PHONY: build
build: install
	cd frontend && yarn build

.PHONY: promote
promote: install
	make test-system CYPRESS_SITE=https://memegen-link-v2-staging.herokuapp.com
	heroku pipelines:promote --app memegen-link-v2-staging --to memegen-link-v2
	make test-system CYPRESS_SITE=https://memegen-link-v2.herokuapp.com
