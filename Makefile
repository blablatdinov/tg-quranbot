# The MIT License (MIT).
#
# Copyright (c) 2018-2024 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
# DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
# OR OTHER DEALINGS IN THE SOFTWARE.

run:
	poetry run python src/main.py run_polling

events:
	poetry run python src/main.py receive_events

fmt:
	poetry run isort src
	poetry run ruff check src --fix-only

lint:
	poetry run isort src
	poetry run ruff check src --fix --output-format=concise
	poetry run flake8 src
	poetry run refurb src
	poetry run fixit src
	poetry run pylint src | poetry run ondivi --only-violations
	poetry run mypy src
	poetry run sqlfluff lint migrations --dialect postgres

test:
	poetry run mypy src
	poetry run pytest src --ignore=src/tests/e2e --cov=src --cov-report html --cov-fail-under=96

e2e:
	poetry run pytest src/tests/e2e -m 'not tg_button'

clean:
	git clean -f -d -x -e .env me.session
