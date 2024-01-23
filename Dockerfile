FROM python:3.12.1-slim as base
ENV PIP_DISABLE_PIP_VERSION_CHECK=1
WORKDIR /app

FROM base as poetry
RUN pip install poetry==1.7.1
COPY poetry.lock pyproject.toml /app/
RUN poetry export --without dev -o requirements.txt

FROM base as build
COPY --from=poetry /app/requirements.txt /tmp/requirements.txt
RUN cat /tmp/requirements.txt
RUN apt-get update && apt-get install gcc -y
RUN python -m venv /app/.venv && /app/.venv/bin/pip install -r /tmp/requirements.txt

FROM python:3.12.1-slim as runtime

# Copy only requirements to cache them in docker layer
WORKDIR /app
COPY --from=build /app/.venv /app/.venv

# Creating folders, and files for a project:
COPY src/app /app
