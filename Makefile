.PHONY: all
all: install

.PHONY: ci
ci: format check test

###############################################################################
# System Dependencies

.PHONY: doctor
doctor:
	bin/verchew --exit-code

.envrc:
	echo export TBD_SERVERLESS_TOKEN=??? >> $@
	echo >> $@
	echo export BROWSER=firefox >> $@
	direnv allow

###############################################################################
# Project Dependencies

BACKEND_DEPENDENCIES := .venv/.flag
FRONTEND_DEPENDENCIES := frontend/node_modules/.flag
SERVICE_DEPENDENCIES := service/node_modules/.flag

.PHONY: install
install: $(BACKEND_DEPENDENCIES) $(FRONTEND_DEPENDENCIES) $(SERVICE_DEPENDENCIES)

$(BACKEND_DEPENDENCIES): poetry.lock
	@ poetry config settings.virtualenvs.in-project true || poetry config virtualenvs.in-project true
	poetry install
	@ poetry run pip freeze > requirements.txt
	@ grep -v memegen requirements.txt > requirements.txt.tmp
	@ mv requirements.txt.tmp requirements.txt
	@ touch $@

$(FRONTEND_DEPENDENCIES): frontend/yarn.lock
	cd frontend && yarn install
	@ touch $@

$(SERVICE_DEPENDENCIES): service/yarn.lock
	cd service && yarn install
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
	@ echo
	@ echo "All system tests passed."

.PHONY: watch
watch: install
	poetry run pytest-watch --nobeep --runner="make test CYPRESS_SITE=http://localhost:5000" --onpass="make check && clear && echo 'All tests passed.'"

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
	cd backend && poetry run coveragespace jacebrowning/memegen-v2 overall

# Frontend

.PHONY: test-frontend
test-frontend: install
	cd frontend && CI=true yarn test

# Service

.PHONY: test-service
test-service: install
	cd service && sls test

# Tools

.PHONY: cypress
cypress: install
	cd frontend && yarn run cypress open

###############################################################################
# Migration Tasks

.PHONY: import
import: install
	poetry run gitman update --force --quiet
	poetry run python backend/import_legacy_templates.py

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
