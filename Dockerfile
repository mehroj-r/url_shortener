ARG PYTHON_VERSION=3.13.3

# ---- Stage 1: Builder ----
FROM python:${PYTHON_VERSION}-alpine AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apk update

WORKDIR /app_build

RUN pip install --no-cache-dir --upgrade pip setuptools wheel

COPY pyproject.toml uv.lock ./

RUN pip install --no-cache-dir --prefix=/python_deps .

COPY . .

# ---- Stage 2: Final runtime image ----
FROM python:${PYTHON_VERSION}-alpine AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    APP_PORT=8000

ENV PYTHONPATH=/app:/python_deps/lib/python3.13/site-packages
ENV PATH=/python_deps/bin:$PATH

RUN apk update

WORKDIR /app

COPY --from=builder /python_deps /python_deps
COPY --from=builder /app_build/src ./

EXPOSE $APP_PORT
RUN chmod +x ./scripts/entrypoint.sh