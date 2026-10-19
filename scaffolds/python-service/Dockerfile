# syntax=docker/dockerfile:1.7
# One Python image for migrate, api and worker: the locked runtime dependencies, no dev tools,
# no secrets (they arrive at run time through compose's env_file).

FROM ghcr.io/astral-sh/uv:0.9.27 AS uv

FROM python:3.12-slim AS build
COPY --from=uv /uv /bin/uv
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never \
    UV_PROJECT_ENVIRONMENT=/srv/.venv
WORKDIR /srv
# Dependencies first: this layer changes only with uv.lock or a member's pyproject.
COPY pyproject.toml uv.lock ./
COPY app/pyproject.toml app/
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-dev --no-install-workspace
COPY app/src app/src
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-dev --no-editable

FROM python:3.12-slim AS runtime
ENV PATH=/srv/.venv/bin:$PATH \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1
RUN groupadd --system app && useradd --system --gid app --home-dir /srv app
WORKDIR /srv
COPY --from=build /srv/.venv /srv/.venv
COPY alembic.ini ./
COPY app/src/app/persistence/migrations app/src/app/persistence/migrations
USER app
CMD ["appctl", "--help"]
