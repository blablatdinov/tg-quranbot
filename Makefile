run:
	poetry run python src/main.py run_polling

lint:
	poetry run isort src
	poetry run flake8 src
	poetry run mypy src

test:
	poetry run pytest src/tests/unit

cov:
	poetry run pytest src --cov=src
	poetry run coverage html
