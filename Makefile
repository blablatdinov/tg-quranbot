run:
	python src/main.py run_polling

lint:
	isort src && flake8 src

test:
	pytest src --ignore=src/tests/integration/

cov:
	pytest src --cov=src
