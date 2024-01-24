run:
	poetry run python src/manage.py runserver

lint:
	poetry run isort src
	poetry run ruff check src --fix
	# poetry run flake8 src
	poetry run refurb src
	# poetry run mypy src

test:
	poetry run pytest
