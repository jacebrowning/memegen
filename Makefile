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
	echo >> $@
	echo "# export CYPRESS_BASE_URL=http://localhost:5000" >> $@
	direnv allow

###############################################################################
# Project Dependencies

BACKEND_DEPENDENCIES := .venv/.flag
FRONTEND_DEPENDENCIES := frontend/node_modules/.flag
SERVICE_DEPENDENCIES := service/node_modules/.flag

.PHONY: install
install: $(BACKEND_DEPENDENCIES) $(FRONTEND_DEPENDENCIES) $(SERVICE_DEPENDENCIES)

$(BACKEND_DEPENDENCIES): poetry.lock runtime.txt requirements.txt
	@ poetry config virtualenvs.in-project true
	poetry install
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
runtime.txt: .python-version
	echo "python-$(shell cat $<)" > $@
requirements.txt: poetry.lock
	poetry export --format requirements.txt --output $@ --without-hashes
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

.PHONY: watch
watch: install
	poetry run pytest-watch --runner="make test CYPRESS_BASE_URL=http://localhost:5000" --onpass="make check && clear && echo 'All tests passed.'" --nobeep --wait

# Backend

.PHONY: format-backend
format-backend: install
	poetry run autoflake --recursive backend --in-place
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

# System

.PHONY: test-system
test-system: install
ifdef CYPRESS_BASE_URL
	cd frontend && yarn run cypress run
else
	poetry run honcho start --procfile Procfile.e2e
endif
	@ echo
	@ echo "All system tests passed."

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
	make test-system CYPRESS_BASE_URL=https://memegen-link-v2-staging.herokuapp.com
	heroku pipelines:promote --app memegen-link-v2-staging --to memegen-link-v2
	make test-system CYPRESS_BASE_URL=https://memegen-link-v2.herokuapp.com
