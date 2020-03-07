# Project settings
PROJECT := memegen
PACKAGE := memegen
REPOSITORY := jacebrowning/memegen

# Project paths
PACKAGES := $(PACKAGE) tests scripts
CONFIG := $(wildcard *.py)
MODULES := $(wildcard $(PACKAGE)/*.py)

# Virtual environment paths
export PIPENV_SHELL_COMPAT=true
export PIPENV_VENV_IN_PROJECT=true
export PIPENV_IGNORE_VIRTUALENVS=true
ENV := .venv

# MAIN TASKS ###################################################################

SNIFFER := pipenv run sniffer

.PHONY: all
all: install

.PHONY: ci
ci: check test validate ## Run all tasks that determine CI status

.PHONY: validate
validate: install
	FLASK_ENV=test pipenv run python manage.py validate

.PHONY: watch
watch: install .clean-test ## Continuously run all CI tasks when files chanage
	$(SNIFFER)

# SERVER TARGETS ###############################################################

.PHONY: run
run: install samples ## Run the application
	FLASK_ENV=local pipenv run python main.py

.PHONY: launch
launch: install samples
	sleep 3 && open http://localhost:5000 &
	make run

.PHONY: samples
samples: install
	PYTHONPATH=. pipenv run python scripts/generate_sample_images.py

.PHONY: run-production
run-production: install .env
	pipenv shell "bin/post_compile; exit \$$?"
	pipenv shell "heroku local web=1; exit \$$?"

.PHONY: launch-production
launch-production: install
	sleep 5 && open http://localhost:5000 &
	make run-production

# SYSTEM DEPENDENCIES ##########################################################

.PHONY: doctor
doctor:  ## Confirm system dependencies are available
	bin/verchew

.env:
	echo "FLASK_ENV=local" >> $@
	echo "GOOGLE_ANALYTICS_TID=local" >> $@
	echo "#REGENERATE_IMAGES=true" >> $@
	echo "WATERMARK_OPTIONS=localhost" >> $@

# PROJECT DEPENDENCIES #########################################################

DEPENDENCIES := $(ENV)/.pipenv-$(shell bin/checksum Pipfile*)
METADATA := *.egg-info

.PHONY: install
install: $(DEPENDENCIES)

$(DEPENDENCIES):
	pipenv install --dev
	@ touch $@

# CHECKS #######################################################################

PYLINT := pipenv run pylint
PYCODESTYLE := pipenv run pycodestyle
PYDOCSTYLE := pipenv run pydocstyle

.PHONY: check
check: pylint pycodestyle pydocstyle ## Run linters and static analysis

.PHONY: pylint
pylint: install
	$(PYLINT) $(PACKAGES) $(CONFIG) --rcfile=.pylint.ini

.PHONY: pycodestyle
pycodestyle: install
	$(PYCODESTYLE) $(PACKAGES) $(CONFIG) --config=.pycodestyle.ini

.PHONY: pydocstyle
pydocstyle: install
	$(PYDOCSTYLE) $(PACKAGES) $(CONFIG)

# TESTS ########################################################################

PYTEST := pipenv run pytest
COVERAGE := pipenv run coverage
COVERAGESPACE := pipenv run coveragespace

RANDOM_SEED ?= $(shell date +%s)
FAILURES := .cache/v/cache/lastfailed
PYTEST_CORE_OPTIONS := -ra -vv
PYTEST_COV_OPTIONS := --cov=$(PACKAGE) --no-cov-on-fail --cov-report=term-missing:skip-covered --cov-report=html
PYTEST_RANDOM_OPTIONS := --random --random-seed=$(RANDOM_SEED)

PYTEST_OPTIONS := $(PYTEST_CORE_OPTIONS) $(PYTEST_RANDOM_OPTIONS)
ifndef DISABLE_COVERAGE
PYTEST_OPTIONS += $(PYTEST_COV_OPTIONS)
endif
PYTEST_RERUN_OPTIONS := $(PYTEST_CORE_OPTIONS) --last-failed --exitfirst

.PHONY: test
test: test-all ## Run unit and integration tests

.PHONY: test-unit
test-unit: install
	@ ( mv $(FAILURES) $(FAILURES).bak || true ) > /dev/null 2>&1
	$(PYTEST) $(PYTEST_OPTIONS) $(PACKAGE)
	@ ( mv $(FAILURES).bak $(FAILURES) || true ) > /dev/null 2>&1
	$(COVERAGESPACE) $(REPOSITORY) unit

.PHONY: test-int
test-int: install
	@ if test -e $(FAILURES); then $(PYTEST) $(PYTEST_RERUN_OPTIONS) tests; fi
	@ rm -rf $(FAILURES)
	$(PYTEST) $(PYTEST_OPTIONS) tests
	$(COVERAGESPACE) $(REPOSITORY) integration

.PHONY: test-all
test-all: install
	@ if test -e $(FAILURES); then $(PYTEST) $(PYTEST_RERUN_OPTIONS) $(PACKAGES); fi
	@ rm -rf $(FAILURES)
	$(PYTEST) $(PYTEST_OPTIONS) $(PACKAGES)
	$(COVERAGESPACE) $(REPOSITORY) overall

.PHONY: read-coverage
read-coverage:
	bin/open htmlcov/index.html

# CLEANUP ######################################################################

.PHONY: clean
clean: .clean-images .clean-test .clean-build ## Delete all generated and temporary files

.PHONY: clean-all
clean-all: clean .clean-env .clean-workspace  ## Delete the virtual environment

.PHONY: .clean-build
.clean-build:
	find $(PACKAGES) -name '*.pyc' -delete
	find $(PACKAGES) -name '__pycache__' -delete
	rm -rf *.egg-info

.PHONY: .clean-test
.clean-test:
	rm -rf .cache .pytest .coverage htmlcov

.PHONY: .clean-images
.clean-images:
	find data/images -name "*.img" -delete

.PHONY: .clean-env
.clean-env: clean
	rm -rf $(ENV)

.PHONY: .clean-workspace
.clean-workspace:
	find data/templates -name '*.tmp' -delete
	rm -rf *.sublime-workspace

# HELP #########################################################################

.PHONY: help
help: all
	@ grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

.DEFAULT_GOAL := help
