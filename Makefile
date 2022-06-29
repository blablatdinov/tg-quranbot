run:
	python src/main.py

lint:
	isort src && flake8 src

test:
	pytest

cov:
	pytest --cov=src
