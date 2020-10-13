export PYTHONBREAKPOINT=ipdb.set_trace

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

.PHONY: clean-all
clean-all: clean
	rm -rf *.egg-info .venv

###############################################################################
# Development Tasks

PACKAGES := app scripts

.PHONY: run
run: install
	DEBUG=true poetry run python app/views.py

.PHONY: format
format: install
	poetry run autoflake --recursive $(PACKAGES) --in-place --remove-all-unused-imports --ignore-init-module-imports
	poetry run isort $(PACKAGES)
	poetry run black $(PACKAGES)

.PHONY: check
check: install
	poetry run mypy $(PACKAGES)

.PHONY: test
test: install
ifdef CI
	poetry run pytest --verbose --junit-xml=results/junit.xml
else
	@ if test -e .cache/v/cache/lastfailed; then \
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
	poetry run coveragespace jacebrowning/memegen unit
else
	poetry run coveragespace jacebrowning/memegen overall
endif

.PHONY: test-fast
test-fast: install
	poetry run pytest -m "not slow" --durations=10

.PHONY: test-slow
test-slow: install
	poetry run pytest -m slow --durations=0

.PHONY: watch
watch: install
	@ sleep 2 && touch */__init__.py &
	@ poetry run watchmedo shell-command --recursive --pattern="*.py;*.yml" --command="clear && make test check format SKIP_SLOW=true && echo && echo ✅ && echo" --wait --drop

###############################################################################
# Delivery Tasks

.PHONY: run-production
run-production: install .env
	poetry run heroku local --showenvs

.env:
	echo WEB_CONCURRENCY=2 >> $@
	echo MAX_REQUESTS=0 >> $@
	echo MAX_REQUESTS_JITTER=0 >> $@

.PHONY: promote
promote: install
	SITE=https://staging-api.memegen.link poetry run pytest scripts/check_deployment.py --verbose --no-cov --reruns=2
	@ echo
	heroku pipelines:promote --app memegen-link-staging --to memegen-link
	@ echo
	SITE=https://api.memegen.link poetry run pytest scripts/check_deployment.py --verbose --no-cov --reruns=2
