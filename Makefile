run:
	# poetry run uvicorn src.app.main:app --reload --log-level=debug
	poetry run litestar --app src.app.main:app run -d

lint:
	poetry run isort src tests
	poetry run ruff check src tests --fix
	poetry run flake8 src tests
	poetry run refurb src tests
	poetry run mypy src tests

test:
	poetry run pytest
