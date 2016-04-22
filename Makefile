# Project settings
PROJECT := MemeGen
PACKAGE := memegen
DIRECTORIES := $(PACKAGE) tests scripts
FILES := Makefile $(shell find $(DIRECTORIES) -name '*.py')

# Python settings
ifndef TRAVIS
	PYTHON_MAJOR ?= 3
	PYTHON_MINOR ?= 5
endif

# System paths
PLATFORM := $(shell python -c 'import sys; print(sys.platform)')
ifneq ($(findstring darwin, $(PLATFORM)), )
	MAC := 1
else
	LINUX := 1
endif
SYS_PYTHON := python$(PYTHON_MAJOR)
ifdef PYTHON_MINOR
	SYS_PYTHON := $(SYS_PYTHON).$(PYTHON_MINOR)
endif

# Virtual environment paths
ENV := env
BIN := $(ENV)/bin
ACTIVATE := . $(BIN)/activate
OPEN := open

# Virtual environment executables
ifndef TRAVIS
	BIN_ := $(BIN)/
endif
PYTHON := $(BIN_)python
PIP := $(BIN_)pip
EASY_INSTALL := $(BIN_)easy_install
RST2HTML := $(PYTHON) $(BIN_)rst2html.py
PDOC := $(PYTHON) $(BIN_)pdoc
MKDOCS := $(BIN_)mkdocs
PEP8 := $(BIN_)pep8
PEP8RADIUS := $(BIN_)pep8radius
PEP257 := $(BIN_)pep257
PYLINT := $(BIN_)pylint
PYREVERSE := $(BIN_)pyreverse
NOSE := $(BIN_)nosetests
PYTEST := $(BIN_)py.test
COVERAGE := $(BIN_)coverage
COVERAGE_SPACE := $(BIN_)coverage.space
SNIFFER := $(BIN_)sniffer
HONCHO := PYTHONPATH=$(PWD) $(ACTIVATE) && $(BIN_)honcho

# Flags for PHONY targets
INSTALLED_FLAG := $(ENV)/.installed
DEPENDS_CI_FLAG := $(ENV)/.depends-ci
DEPENDS_DOC_FLAG := $(ENV)/.depends-doc
DEPENDS_DEV_FLAG := $(ENV)/.depends-dev
DOCS_FLAG := $(ENV)/.docs
ALL_FLAG := $(ENV)/.all

# Main Targets #################################################################

IP = $(shell ipconfig getifaddr en0 || ipconfig getifaddr en1)
CONFIG ?= dev
PORT := 5000

.PHONY: all
all: depends doc $(ALL_FLAG)
$(ALL_FLAG): $(FILES)
	$(MAKE) check
	touch $(ALL_FLAG)  # flag to indicate all setup steps were successful

.PHONY: ci
ci: check test tests validate

.PHONY: run
run: .env env depends db-dev
	$(HONCHO) run bin/post_compile
	$(HONCHO) start

.PHONY: launch
launch: env depends
	eval "sleep 5; open http://$(IP):$(PORT)" &
	$(MAKE) run

.PHONY: gui
gui: .env env depends
ifdef MAC
	brew install flac portaudio swig
endif
	$(PIP) install speechrecognition pyaudio pocketsphinx
	$(HONCHO) run scripts/run_gui.py

.PHONY: validate
validate: env
	CONFIG=test $(PYTHON) manage.py validate

.PHONY: watch
watch: depends .clean-test
	@ rm -rf $(FAILED_FLAG)
	$(SNIFFER)

# Environment Setup ############################################################

.env:
	echo "CONFIG=dev" >> $@
	echo "#REGENERATE_IMAGES=true" >> $@
	echo "DATABASE_URL=postgresql://localhost/memegen_dev" >> $@
	echo "GOOGLE_ANALYTICS_TID=local" >> $@

.PHONY: db-dev
db-dev:
	@ if ! psql memegen_dev -c "";            \
	then                                      \
		echo "Creating database memegen_dev"; \
		createdb memegen_dev;                 \
	fi;
	$(MAKE) upgrade

# Database Migrations ##########################################################

.PHONY: migrate
migrate: depends
	$(PYTHON) manage.py db migrate

.PHONY: upgrade
upgrade: depends
	$(PYTHON) manage.py db upgrade

.PHONY: downgrade
downgrade: depends
	$(PYTHON) manage.py db downgrade

# Development Installation #####################################################

.PHONY: env
env: $(PIP) $(INSTALLED_FLAG)
$(INSTALLED_FLAG): Makefile setup.py requirements.txt
	$(PYTHON) setup.py develop
	@ touch $@  # flag to indicate package is installed

$(PIP):
	$(SYS_PYTHON) -m venv --clear $(ENV)
ifndef APPVEYOR
	$(PIP) install --upgrade pip setuptools
endif

# Tools Installation ###########################################################

.PHONY: depends
depends: depends-ci depends-doc depends-dev

.PHONY: depends-ci
depends-ci: env Makefile $(DEPENDS_CI_FLAG)
$(DEPENDS_CI_FLAG): Makefile
	$(PIP) install --upgrade pep8 pep257 pylint coverage coverage.space pytest pytest-describe pytest-expecter pytest-cov pytest-random testing.postgresql
	@ touch $(DEPENDS_CI_FLAG)  # flag to indicate dependencies are installed

.PHONY: depends-doc
depends-doc: env Makefile $(DEPENDS_DOC_FLAG)
$(DEPENDS_DOC_FLAG): Makefile
	$(PIP) install --upgrade pylint docutils readme pdoc mkdocs pygments
	@ touch $(DEPENDS_DOC_FLAG)  # flag to indicate dependencies are installed

.PHONY: depends-dev
depends-dev: env Makefile $(DEPENDS_DEV_FLAG)
$(DEPENDS_DEV_FLAG): Makefile
	$(PIP) install --upgrade pip pep8radius wheel sniffer honcho
ifdef MAC
	$(PIP) install --upgrade pync MacFSEvents==0.4
else ifdef LINUX
	$(PIP) install --upgrade pyinotify
endif
	@ touch $(DEPENDS_DEV_FLAG)  # flag to indicate dependencies are installed

# Documentation ################################################################

.PHONY: doc
doc: readme uml

.PHONY: doc-live
doc-live: doc
	eval "sleep 3; open http://127.0.0.1:8000" &
	$(MKDOCS) serve

.PHONY: read
read: doc
	$(OPEN) site/index.html
	$(OPEN) apidocs/$(PACKAGE)/index.html
	$(OPEN) README-pypi.html
	$(OPEN) README-github.html

.PHONY: readme
readme: depends-doc README-github.html README-pypi.html
README-github.html: README.md
	pandoc -f markdown_github -t html -o README-github.html README.md
README-pypi.html: README.rst
	$(RST2HTML) README.rst README-pypi.html
%.rst: %.md
	pandoc -f markdown_github -t rst -o $@ $<

.PHONY: verify-readme
verify-readme: $(DOCS_FLAG)
$(DOCS_FLAG): README.rst CHANGELOG.rst
	$(PYTHON) setup.py check --restructuredtext --strict --metadata
	@ touch $(DOCS_FLAG)  # flag to indicate README has been checked

.PHONY: uml
uml: depends-doc docs/*.png
docs/*.png: $(FILES)
	$(PYREVERSE) $(PACKAGE) -p $(PACKAGE) -a 1 -f ALL -o png --ignore test
	- mv -f classes_$(PACKAGE).png docs/classes.png
	- mv -f packages_$(PACKAGE).png docs/packages.png

.PHONY: apidocs
apidocs: depends-doc apidocs/$(PACKAGE)/index.html
apidocs/$(PACKAGE)/index.html: $(FILES)
	$(PDOC) --html --overwrite $(PACKAGE) --html-dir apidocs

.PHONY: mkdocs
mkdocs: depends-doc site/index.html
site/index.html: mkdocs.yml docs/*.md
	$(MKDOCS) build --clean --strict

# Static Analysis ##############################################################

.PHONY: check
check: pep8 pep257 pylint

.PHONY: pep8
pep8: depends-ci
	$(PEP8) $(DIRECTORIES) --config=.pep8rc

.PHONY: pep257
pep257: depends-ci
	$(PEP257) $(DIRECTORIES)

.PHONY: pylint
pylint: depends-ci
	$(PYLINT) $(DIRECTORIES) --rcfile=.pylintrc

.PHONY: fix
fix: depends-dev
	$(PEP8RADIUS) --docformatter --in-place

# Testing ######################################################################

RANDOM_SEED ?= $(shell date +%s)

PYTEST_CORE_OPTS := -r xXw -vv
PYTEST_COV_OPTS := --cov=$(PACKAGE) --no-cov-on-fail --cov-report=term-missing --cov-report=html
PYTEST_RANDOM_OPTS := --random --random-seed=$(RANDOM_SEED)

PYTEST_OPTS := $(PYTEST_CORE_OPTS) $(PYTEST_COV_OPTS) $(PYTEST_RANDOM_OPTS)
PYTEST_OPTS_FAILFAST := $(PYTEST_OPTS) --last-failed --exitfirst

FAILURES := .cache/v/cache/lastfailed

.PHONY: test test-unit
test: test-unit
test-unit: depends-ci
	@- mv $(FAILURES) $(FAILURES).bak
	$(PYTEST) $(PYTEST_OPTS) $(PACKAGE)
	@- mv $(FAILURES).bak $(FAILURES)
ifndef TRAVIS
ifndef APPVEYOR
	$(COVERAGE_SPACE) jacebrowning/memegen unit
endif
endif

.PHONY: test-int
test-int: depends-ci
	@ if test -e $(FAILURES); then $(PYTEST) $(PYTEST_OPTS_FAILFAST) tests; fi
	$(PYTEST) $(PYTEST_OPTS) tests
ifndef TRAVIS
ifndef APPVEYOR
	$(COVERAGE_SPACE) jacebrowning/memegen integration
endif
endif

.PHONY: tests test-all
tests: test-all
test-all: depends-ci
	@ if test -e $(FAILURES); then $(PYTEST) $(PYTEST_OPTS_FAILFAST) $(PACKAGE) tests; fi
	$(PYTEST) $(PYTEST_OPTS) $(PACKAGE) tests
ifndef TRAVIS
ifndef APPVEYOR
	$(COVERAGE_SPACE) jacebrowning/memegen overall
endif
endif

.PHONY: read-coverage
read-coverage:
	$(OPEN) htmlcov/index.html

# Cleanup ######################################################################

.PHONY: clean
clean: .clean-dist .clean-test .clean-doc .clean-build
	rm -rf $(ALL_FLAG)

.PHONY: clean-all
clean-all: clean .clean-env .clean-workspace

.PHONY: .clean-build
.clean-build:
	find $(DIRECTORIES) -name '*.pyc' -delete
	find $(DIRECTORIES) -name '__pycache__' -delete
	rm -rf $(INSTALLED_FLAG) *.egg-info

.PHONY: .clean-doc
.clean-doc:
	rm -rf README.rst apidocs *.html docs/*.png site

.PHONY: .clean-test
.clean-test:
	rm -rf .cache .pytest .coverage htmlcov

.PHONY: .clean-dist
.clean-dist:
	rm -rf dist build

.PHONY: .clean-env
.clean-env: clean
	rm -rf $(ENV)

.PHONY: .clean-workspace
.clean-workspace:
	find data -name '*.tmp' -delete
	rm -rf *.sublime-workspace
