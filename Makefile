all: lint test

PACKAGES = iliad tests

.PHONY: lint
lint: .venv
	poetry run mypy $(PACKAGES)
	poetry run flake8 $(PACKAGES)
	poetry run isort --check-only --profile black $(PACKAGES)
	poetry run black --check --diff $(PACKAGES)

.PHONY: fmt
fmt: .venv
	poetry run isort --profile black $(PACKAGES)
	poetry run black $(PACKAGES)

.PHONY: test
test: .venv
	poetry run pytest --verbose --capture=no

.PHONY: publish
publish: dist
	poetry publish

dist: .venv
	poetry build

.venv: poetry.lock
	poetry install
	cd .venv/lib/*/site-packages/tomlkit ; touch py.typed
	@touch -c .venv

poetry.lock: pyproject.toml
	poetry lock
	@touch -c poetry.lock
