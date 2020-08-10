.PHONEY: lint fmt test publish

lint: .venv
	poetry run flake8 --exclude .venv
	poetry run isort --check-only --profile black .
	poetry run black --check --diff .

fmt: .venv
	poetry run isort --profile black .
	poetry run black .

test: .venv
	poetry run pytest --verbose --capture=no

publish: dist
	poetry publish

dist: .venv
	poetry build

.venv: poetry.lock
	poetry install
	@touch -c .venv

poetry.lock: pyproject.toml
	poetry update
	@touch -c poetry.lock
