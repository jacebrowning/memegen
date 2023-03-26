export PYTHONBREAKPOINT=ipdb.set_trace

.PHONY: all
all: doctor format check test ## Run all validation targets

.PHONY: dev
dev: install ## Rerun all validation targests in a loop
	@ sleep 2 && touch */__init__.py &
	@ poetry run watchmedo shell-command --recursive --pattern="*.py" --command="clear && make test check format SKIP_SLOW=true && echo && echo ✅ && echo" --wait --drop

###############################################################################
# System Dependencies

.PHONY: boostrap
boostrap: ## Attempt to install system dependencies
	asdf plugin add python || asdf plugin update python
	asdf plugin add poetry https://github.com/asdf-community/asdf-poetry.git || asdf plugin update poetry
	asdf install

.PHONY: doctor
doctor: ## Check for required system dependencies
	bin/verchew --exit-code

###############################################################################
# Project Dependencies

BACKEND_DEPENDENCIES := .venv/.flag

.PHONY: install
install: $(BACKEND_DEPENDENCIES) ## Install project dependencies

$(BACKEND_DEPENDENCIES): poetry.lock runtime.txt requirements.txt
	@ poetry config virtualenvs.in-project true
ifdef CI
	poetry install
else
	poetry install --extras testing
endif
	@ touch $@

ifndef CI
poetry.lock: pyproject.toml
	poetry lock --no-update
	@ touch $@
runtime.txt: .tool-versions
	echo $(shell grep '^python ' $< | tr ' ' '-') > $@
requirements.txt: poetry.lock
	poetry export --format requirements.txt --output $@ --without-hashes
endif

site: install
	poetry run mkdocs build --strict
	sed -i -e 's/http:\/\/localhost:5000/https:\/\/api.memegen.link/g' site/examples/index.html
	echo memegen.link > site/CNAME
ifeq ($(CIRCLE_BRANCH),main)
	@ echo
	git config --global user.name CircleCI
	poetry run mkdocs gh-deploy --dirty
endif

.PHONY: clean
clean:
	rm -rf images site templates/_custom-* templates/*/_*

.PHONY: clean-all
clean-all: clean
	rm -rf app/tests/images
	rm -rf *.egg-info .venv

###############################################################################
# Development Tasks

PACKAGES := app scripts

.PHONY: format
format: install
	poetry run autoflake --recursive $(PACKAGES) --in-place --remove-all-unused-imports --ignore-init-module-imports
	poetry run isort $(PACKAGES)
	poetry run black $(PACKAGES)

.PHONY: check
check: install ## Run static analysis
	poetry run mypy $(PACKAGES)

.PHONY: test
test: install ## Run all tests
ifdef CI
	poetry run pytest --verbose --junit-xml=results/junit.xml
else
	@ if test -e .cache/pytest/v/cache/lastfailed; then \
		echo "Running failed tests..." && \
		poetry run pytest --last-failed --maxfail=1 --no-cov && \
		echo "Running all tests..." && \
		poetry run pytest --cache-clear; \
	else \
		echo "Running all tests..." && \
		poetry run pytest --new-first --maxfail=1; \
	fi
endif
ifdef SKIP_SLOW
	poetry run coveragespace update unit
else
	poetry run coveragespace update overall
endif

.PHONY: test-fast
test-fast: install
	poetry run pytest -m "not slow" --durations=10

.PHONY: test-slow
test-slow: install
	poetry run pytest -m slow --durations=0 --durations-min=0.05

.PHONY: run
run: install ## Run the applicaiton
	poetry run honcho start --procfile Procfile.dev

###############################################################################
# Delivery Tasks

.PHONY: run-production
run-production: install .env
	poetry run heroku local web

.PHONY: deploy
deploy: .envrc
	@ echo
	git diff --exit-code
	heroku git:remote -a memegen-staging
	@ echo
	git push heroku main

.PHONY: promote
promote: install .envrc
	@ echo
	SITE=https://staging.memegen.link poetry run pytest scripts/check_deployment.py --verbose --no-cov
	@ echo
	heroku pipelines:promote --app memegen-staging --to memegen-production
	@ echo
	sleep 30
	@ echo
	SITE=https://api.memegen.link poetry run pytest scripts/check_deployment.py --verbose --no-cov

.env:
	echo WEB_CONCURRENCY=2 >> $@
	echo MAX_REQUESTS=0 >> $@
	echo MAX_REQUESTS_JITTER=0 >> $@

.envrc:
	echo dotenv >> $@
	echo >> $@
	echo "export CF_API_KEY=???" >> $@
	echo "export REMOTE_TRACKING_URL=???" >> $@
	echo "export DEBUG=true" >> $@

# HELP ########################################################################

.PHONY: help
help: install
	@ grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

.DEFAULT_GOAL := help
