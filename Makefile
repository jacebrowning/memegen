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
	FLASK_CONFIG=test pipenv run python manage.py validate

.PHONY: watch
watch: install .clean-test ## Continuously run all CI tasks when files chanage
	- pipenv run pip install MacFSEvents
	$(SNIFFER)

# SERVER TARGETS ###############################################################

.PHONY: run
run: install ## Run the application
	status=1; while [ $$status -eq 1 ]; do FLASK_ENV=dev pipenv run python manage.py run; status=$$?; sleep 1; done

.PHONY: launch
launch: install
	sleep 3 && open http://localhost:5000 &
	make run

.PHONY: run-prod
run-prod: install .env
	pipenv shell -c "bin/post_compile; exit \$$?"
	pipenv shell -c "heroku local web=1; exit \$$?"

.PHONY: launch-prod
launch-prod: install
	sleep 5 && open http://localhost:5000 &
	make run-prod

# SYSTEM DEPENDENCIES ##########################################################

.PHONY: doctor
doctor:  ## Confirm system dependencies are available
	bin/verchew

.env:
	echo "FLASK_CONFIG=dev" >> $@
	echo "GOOGLE_ANALYTICS_TID=local" >> $@
	echo "#REGENERATE_IMAGES=true" >> $@
	echo "WATERMARK_OPTIONS=localhost" >> $@

# PROJECT DEPENDENCIES #########################################################

DEPENDENCIES := $(ENV)/.installed
METADATA := *.egg-info

.PHONY: install
install: $(DEPENDENCIES)

$(DEPENDENCIES): Pipfile*
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

PYTEST := pipenv run py.test
COVERAGE := pipenv run coverage
COVERAGE_SPACE := pipenv run coverage.space

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
	@- mv $(FAILURES) $(FAILURES).bak
	$(PYTEST) $(PYTEST_OPTIONS) $(PACKAGE)
	@- mv $(FAILURES).bak $(FAILURES)
	$(COVERAGE_SPACE) $(REPOSITORY) unit

.PHONY: test-int
test-int: install
	@ if test -e $(FAILURES); then $(PYTEST) $(PYTEST_RERUN_OPTIONS) tests; fi
	@ rm -rf $(FAILURES)
	$(PYTEST) $(PYTEST_OPTIONS) tests
	$(COVERAGE_SPACE) $(REPOSITORY) integration

.PHONY: test-all
test-all: install
	@ if test -e $(FAILURES); then $(PYTEST) $(PYTEST_RERUN_OPTIONS) $(PACKAGES); fi
	@ rm -rf $(FAILURES)
	$(PYTEST) $(PYTEST_OPTIONS) $(PACKAGES)
	$(COVERAGE_SPACE) $(REPOSITORY) overall

.PHONY: read-coverage
read-coverage:
	bin/open htmlcov/index.html

# CLEANUP ######################################################################

.PHONY: clean
clean: .clean-test .clean-build ## Delete all generated and temporary files

.PHONY: clean-all
clean-all: clean .clean-env .clean-workspace

.PHONY: .clean-build
.clean-build:
	find $(PACKAGES) -name '*.pyc' -delete
	find $(PACKAGES) -name '__pycache__' -delete
	rm -rf *.egg-info

.PHONY: .clean-test
.clean-test:
	rm -rf .cache .pytest .coverage htmlcov

.PHONY: .clean-env
.clean-env: clean
	rm -rf $(ENV)

.PHONY: .clean-workspace
.clean-workspace:
	find data -name '*.tmp' -delete
	rm -rf *.sublime-workspace

# HELP #########################################################################

.PHONY: help
help: all
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

.DEFAULT_GOAL := help
