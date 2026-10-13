ARG PYTHON_VERSION=3.14.7

# ---- Stage 1: Builder ----
FROM python:${PYTHON_VERSION}-alpine AS builder

COPY --from=ghcr.io/astral-sh/uv:0.12.10 /uv /bin/uv

# Dev compose builds with INSTALL_DEV=true to get the debug tools
ARG INSTALL_DEV=false

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never \
    UV_PROJECT_ENVIRONMENT=/opt/venv

WORKDIR /app_build

# Install exactly what uv.lock pins
COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    if [ "$INSTALL_DEV" = "true" ]; then uv sync --frozen; else uv sync --frozen --no-dev; fi

COPY src ./src
RUN uv version --short > src/VERSION && chmod +x src/scripts/entrypoint.sh

# ---- Stage 2: Final runtime image ----
FROM python:${PYTHON_VERSION}-alpine AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH=/opt/venv/bin:$PATH

RUN addgroup -S -g 1000 app && adduser -S -u 1000 -G app app

WORKDIR /app

COPY --from=builder /opt/venv /opt/venv
COPY --from=builder --chown=app:app /app_build/src ./
RUN mkdir -p staticfiles && chown app:app staticfiles

USER app

EXPOSE 8000

CMD ["gunicorn", "config.wsgi:application", "--config", "python:config.gunicorn"]
