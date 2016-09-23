# Project settings
PROJECT := MemeGen
PACKAGE := memegen
REPOSITORY := jacebrowning/memegen
PACKAGES := $(PACKAGE) tests scripts
CONFIG := $(shell ls *.py)
MODULES := $(shell find $(PACKAGES) -name '*.py') $(CONFIG)

# Python settings
ifndef TRAVIS
	PYTHON_MAJOR ?= 3
	PYTHON_MINOR ?= 5
endif

# System paths
PLATFORM := $(shell python -c 'import sys; print(sys.platform)')
ifneq ($(findstring win32, $(PLATFORM)), )
	WINDOWS := true
	SYS_PYTHON_DIR := C:\\Python$(PYTHON_MAJOR)$(PYTHON_MINOR)
	SYS_PYTHON := $(SYS_PYTHON_DIR)\\python.exe
	# https://bugs.launchpad.net/virtualenv/+bug/449537
	export TCL_LIBRARY=$(SYS_PYTHON_DIR)\\tcl\\tcl8.5
else
	ifneq ($(findstring darwin, $(PLATFORM)), )
		MAC := true
	else
		LINUX := true
	endif
	SYS_PYTHON := python$(PYTHON_MAJOR)
	ifdef PYTHON_MINOR
		SYS_PYTHON := $(SYS_PYTHON).$(PYTHON_MINOR)
	endif
endif

# Virtual environment paths
ENV := env
ifneq ($(findstring win32, $(PLATFORM)), )
	BIN := $(ENV)/Scripts
	ACTIVATE := $(BIN)/activate.bat
	OPEN := cmd /c start
else
	BIN := $(ENV)/bin
	ACTIVATE := . $(BIN)/activate
	ifneq ($(findstring cygwin, $(PLATFORM)), )
		OPEN := cygstart
	else
		OPEN := open
	endif
endif

# Virtual environment executables
ifndef TRAVIS
	BIN_ := $(BIN)/
endif
PYTHON := $(BIN_)python
PIP := $(BIN_)pip
EASY_INSTALL := $(BIN_)easy_install
SNIFFER := $(BIN_)sniffer
HONCHO := $(ACTIVATE) && $(BIN_)honcho

# MAIN TASKS ###################################################################

.PHONY: all
all: doc

.PHONY: ci
ci: check test validate ## Run all tasks that determine CI status

.PHONY: validate
validate: env
	FLASK_CONFIG=test $(PYTHON) manage.py validate

.PHONY: watch
watch: depends .clean-test ## Continuously run all CI tasks when files chanage
	$(SNIFFER)

# SERVER TARGETS ###############################################################

.PHONY: run
run: depends ## Run the application
	status=1; while [ $$status -eq 1 ]; do FLASK_ENV=dev $(PYTHON) manage.py run; status=$$?; sleep 1; done

.PHONY: launch
launch: depends
	sleep 3 && open http://localhost:5000 &
	make run

.PHONY: run-prod
run-prod: depends .env
	$(HONCHO) run bin/post_compile
	$(HONCHO) start

.PHONY: launch-prod
launch-prod: depends
	sleep 5 && open http://localhost:5000 &
	make run-prod

# SYSTEM DEPENDENCIES ##########################################################

.PHONY: doctor
doctor:  ## Confirm system dependencies are available
	@ echo "Checking Python version:"
	@ python --version | tee /dev/stderr | grep -q "3.5."

.env:
	echo "FLASK_CONFIG=dev" >> $@
	echo "#REGENERATE_IMAGES=true" >> $@
	echo "GOOGLE_ANALYTICS_TID=local" >> $@

# PROJECT DEPENDENCIES #########################################################

DEPENDS := $(ENV)/.depends
DEPENDS_CI := $(ENV)/.depends-ci
DEPENDS_DEV := $(ENV)/.depends-dev

env: $(PYTHON)

$(PYTHON):
	$(SYS_PYTHON) -m venv $(ENV)
	$(PYTHON) -m pip install --upgrade pip setuptools

.PHONY: depends
depends: env $(DEPENDS) $(DEPENDS_CI) $(DEPENDS_DEV) ## Install all project dependnecies

$(DEPENDS): setup.py requirements.txt
	$(PYTHON) setup.py develop
	@ touch $@  # flag to indicate dependencies are installed

$(DEPENDS_CI): requirements/ci.txt
	$(PIP) install --upgrade -r $^
	@ touch $@  # flag to indicate dependencies are installed

$(DEPENDS_DEV): requirements/dev.txt
	$(PIP) install --upgrade -r $^
ifdef WINDOWS
	@ echo "Manually install pywin32: https://sourceforge.net/projects/pywin32/files/pywin32"
else ifdef MAC
	$(PIP) install --upgrade pync MacFSEvents
else ifdef LINUX
	$(PIP) install --upgrade pyinotify
endif
	@ touch $@  # flag to indicate dependencies are installed

# CHECKS #######################################################################

PEP8 := $(BIN_)pep8
PEP8RADIUS := $(BIN_)pep8radius
PEP257 := $(BIN_)pep257
PYLINT := $(BIN_)pylint

.PHONY: check
check: pep8 pep257 pylint ## Run linters and static analysis

.PHONY: pep8
pep8: depends ## Check for convention issues
	$(PEP8) $(PACKAGES) $(CONFIG) --config=.pep8rc

.PHONY: pep257
pep257: depends ## Check for docstring issues
	$(PEP257) $(PACKAGES) $(CONFIG)

.PHONY: pylint
pylint: depends ## Check for code issues
	$(PYLINT) $(PACKAGES) $(CONFIG) --rcfile=.pylintrc

.PHONY: fix
fix: depends
	$(PEP8RADIUS) --docformatter --in-place

# TESTS ########################################################################

PYTEST := $(BIN_)py.test
COVERAGE := $(BIN_)coverage
COVERAGE_SPACE := $(BIN_)coverage.space

RANDOM_SEED ?= $(shell date +%s)

PYTEST_CORE_OPTS := -r xXw -vv
PYTEST_COV_OPTS := --cov=$(PACKAGE) --no-cov-on-fail --cov-report=term-missing --cov-report=html
PYTEST_RANDOM_OPTS := --random --random-seed=$(RANDOM_SEED)

PYTEST_OPTS := $(PYTEST_CORE_OPTS) $(PYTEST_COV_OPTS) $(PYTEST_RANDOM_OPTS)
PYTEST_OPTS_FAILFAST := $(PYTEST_OPTS) --last-failed --exitfirst

FAILURES := .cache/v/cache/lastfailed

.PHONY: test
test: test-all

.PHONY: test-unit
test-unit: depends ## Run the unit tests
	@- mv $(FAILURES) $(FAILURES).bak
	$(PYTEST) $(PYTEST_OPTS) $(PACKAGE)
	@- mv $(FAILURES).bak $(FAILURES)
ifndef TRAVIS
ifndef APPVEYOR
	$(COVERAGE_SPACE) $(REPOSITORY) unit
endif
endif

.PHONY: test-int
test-int: depends ## Run the integration tests
	@ if test -e $(FAILURES); then $(PYTEST) $(PYTEST_OPTS_FAILFAST) tests; fi
	$(PYTEST) $(PYTEST_OPTS) tests
ifndef TRAVIS
ifndef APPVEYOR
	$(COVERAGE_SPACE) $(REPOSITORY) integration
endif
endif

.PHONY: test-all
test-all: depends ## Run all the tests
	@ if test -e $(FAILURES); then $(PYTEST) $(PYTEST_OPTS_FAILFAST) $(PACKAGES); fi
	$(PYTEST) $(PYTEST_OPTS) $(PACKAGES)
ifndef TRAVIS
ifndef APPVEYOR
	$(COVERAGE_SPACE) $(REPOSITORY) overall
endif
endif

.PHONY: read-coverage
read-coverage:
	$(OPEN) htmlcov/index.html

# DOCUMENTATION ################################################################

PYREVERSE := $(BIN_)pyreverse
PDOC := $(PYTHON) $(BIN_)pdoc
MKDOCS := $(BIN_)mkdocs

PDOC_INDEX := docs/apidocs/$(PACKAGE)/index.html
MKDOCS_INDEX := site/index.html

.PHONY: doc
doc: uml ## Run documentation generators

.PHONY: uml
uml: depends docs/*.png ## Generate UML diagrams for classes and packages
docs/*.png: $(MODULES)
	$(PYREVERSE) $(PACKAGE) -p $(PACKAGE) -a 1 -f ALL -o png --ignore tests
	- mv -f classes_$(PACKAGE).png docs/classes.png
	- mv -f packages_$(PACKAGE).png docs/packages.png

.PHONY: pdoc
pdoc: depends $(PDOC_INDEX)  ## Generate API documentaiton with pdoc
$(PDOC_INDEX): $(MODULES)
	$(PDOC) --html --overwrite $(PACKAGE) --html-dir docs/apidocs
	@ touch $@

.PHONY: mkdocs
mkdocs: depends $(MKDOCS_INDEX) ## Build the documentation site with mkdocs
$(MKDOCS_INDEX): mkdocs.yml docs/*.md
	ln -sf `realpath CHANGELOG.md --relative-to=docs/about` docs/about/changelog.md
	ln -sf `realpath CONTRIBUTING.md --relative-to=docs/about` docs/about/contributing.md
	ln -sf `realpath LICENSE.md --relative-to=docs/about` docs/about/license.md
	$(MKDOCS) build --clean --strict

.PHONY: mkdocs-live
mkdocs-live: mkdocs ## Launch and continuously rebuild the mkdocs site
	eval "sleep 3; open http://127.0.0.1:8000" &
	$(MKDOCS) serve

# BUILD ########################################################################

PYINSTALLER := $(BIN_)pyinstaller
PYINSTALLER_MAKESPEC := $(BIN_)pyi-makespec

.PHONY: exe
exe: depends $(PROJECT).spec
	# For framework/shared support: https://github.com/yyuu/pyenv/wiki
	$(PYINSTALLER) $(PROJECT).spec --noconfirm --clean

$(PROJECT).spec:
	$(PYINSTALLER_MAKESPEC) $(PACKAGE)/__main__.py --noupx --onefile --windowed --name=$(PROJECT)

# RELEASE ######################################################################

.PHONY: register-test
register-test: README.rst CHANGELOG.rst ## Register the project on the test PyPI
	$(PYTHON) setup.py register --strict --repository https://testpypi.python.org/pypi

.PHONY: register
register: README.rst CHANGELOG.rst ## Register the project on PyPI
	$(PYTHON) setup.py register --strict

.PHONY: upload-test
upload-test: register-test ## Upload the current version to the test PyPI
	$(PYTHON) setup.py sdist upload --repository https://testpypi.python.org/pypi
	$(PYTHON) setup.py bdist_wheel upload --repository https://testpypi.python.org/pypi
	$(OPEN) https://testpypi.python.org/pypi/$(PROJECT)

.PHONY: upload
upload: .git-no-changes register ## Upload the current version to PyPI
	$(PYTHON) setup.py check --restructuredtext --strict --metadata
	$(PYTHON) setup.py sdist upload
	$(PYTHON) setup.py bdist_wheel upload
	$(OPEN) https://pypi.python.org/pypi/$(PROJECT)

.PHONY: .git-no-changes
.git-no-changes:
	@ if git diff --name-only --exit-code;        \
	then                                          \
		echo Git working copy is clean...;        \
	else                                          \
		echo ERROR: Git working copy is dirty!;   \
		echo Commit your changes and try again.;  \
		exit -1;                                  \
	fi;

%.rst: %.md
	pandoc -f markdown_github -t rst -o $@ $<

# CLEANUP ######################################################################

.PHONY: clean
clean: .clean-dist .clean-test .clean-doc .clean-build ## Delete all generated and temporary files

.PHONY: clean-all
clean-all: clean .clean-env .clean-workspace

.PHONY: .clean-build
.clean-build:
	find $(PACKAGES) -name '*.pyc' -delete
	find $(PACKAGES) -name '__pycache__' -delete
	rm -rf *.egg-info

.PHONY: .clean-doc
.clean-doc:
	rm -rf README.rst docs/apidocs *.html docs/*.png site

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

# HELP #########################################################################

.PHONY: help
help: all
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

.DEFAULT_GOAL := help
