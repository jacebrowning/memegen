ENV = ~/.local/share/virtualenvs/memegen-v2-EVy4QWPh

.PHONY: install
install: $(ENV)
$(ENV): Pipfile*
	pipenv install --dev
	@ touch $@

.PHONY: test
test: install
	pipenv run apistar test

.PHONY: run
run: install
	pipenv run apistar run

.PHONY: run-prod
run-prod: install
	pipenv shell "heroku local; exit \$$?"
