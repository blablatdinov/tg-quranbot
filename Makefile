lint:
	poetry run isort revive_code_bot tests
	poetry run flake8 revive_code_bot tests

test:
	poetry run pytest
