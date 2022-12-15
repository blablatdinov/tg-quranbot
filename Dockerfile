FROM python:3.11 as base
ENV PIP_DISABLE_PIP_VERSION_CHECK=1
WORKDIR /app

FROM base as poetry
RUN pip install poetry==1.2.2
COPY poetry.lock pyproject.toml /app/
RUN poetry export --without dev -o requirements.txt

FROM base as build
COPY --from=poetry /app/requirements.txt /tmp/requirements.txt
RUN apt-get install gcc libffi-dev
RUN cat /tmp/requirements.txt
RUN python -m venv /app/.venv && \
    /app/.venv/bin/pip install 'wheel==0.36.2' && \
    /app/.venv/bin/pip install -r /tmp/requirements.txt

FROM python:3.11-alpine as runtime

# Copy only requirements to cache them in docker layer
WORKDIR /app
COPY --from=build /app/.venv /app/.venv

# Creating folders, and files for a project:
COPY src /app
