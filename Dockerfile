# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

FROM python:3.14.3-slim as base
ENV PIP_DISABLE_PIP_VERSION_CHECK=1
ENV POETRY_VIRTUALENVS_IN_PROJECT=true
WORKDIR /app

FROM base as poetry
RUN pip install poetry==2.0.1
COPY poetry.lock pyproject.toml /app/
RUN poetry install --without dev

FROM python:3.14.3-slim as runtime

# Copy only requirements to cache them in docker layer
WORKDIR /app
COPY --from=poetry /app/.venv /app/.venv

# Creating folders, and files for a project:
COPY src /app
