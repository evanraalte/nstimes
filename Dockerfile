# syntax=docker/dockerfile:1
FROM python:3.11-buster as builder

# https://medium.com/@albertazzir/blazing-fast-python-docker-builds-with-poetry-a78a66f5aed0
ENV POETRY_VERSION=1.6.1 \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    HOST="default" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN git version
RUN pip install "poetry==${POETRY_VERSION}"

WORKDIR /app

COPY ./pyproject.toml ./poetry.lock ./
# Cache mounts are not CI friendly
# RUN --mount=type=cache,target=$POETRY_CACHE_DIR poetry install --no-root --no-interaction --no-ansi && rm -rf ${POETRY_CACHE_DIR}

# TODO: separate runtime and devtime (for CI checks)
RUN poetry install --no-root --only main --no-interaction --no-ansi


# TODO: move to slim-buster for runtime
FROM python:3.11-slim-buster as runtime

ENV VIRTUAL_ENV=/app/.venv \
    PATH="/app/.venv/bin:$PATH"

COPY --from=builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}

# Runtime should contain applications
# Devtime should contain integration tests etc
COPY . .
ENV NS_API_TOKEN="not defined"
ENV PYTHONPATH=.
ENTRYPOINT [ "python", "nstimes/server.py" ]
EXPOSE 8000
