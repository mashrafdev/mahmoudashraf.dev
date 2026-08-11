ARG NODE_VERSION=24.14.0
ARG NGINX_VERSION=1.29.5
ARG UV_VERSION=0.12.2
ARG PYTHON_VERSION=3.14.6

# --- Frontend base ---
FROM node:${NODE_VERSION}-bookworm-slim AS frontend-base

ENV PNPM_HOME=/pnpm
ENV PATH=$PNPM_HOME:$PATH

RUN corepack enable \
    && corepack prepare pnpm@11.20.0 --activate

WORKDIR /app

# --- Production node_modules ---
FROM frontend-base AS frontend-prod-deps

COPY package.json pnpm-lock.yaml pnpm-workspace.yaml ./

RUN --mount=type=cache,id=pnpm,target=/pnpm/store \
    pnpm install --prod --frozen-lockfile

# --- Frontend build ---
FROM frontend-base AS frontend

COPY package.json pnpm-lock.yaml pnpm-workspace.yaml ./

RUN --mount=type=cache,id=pnpm,target=/pnpm/store \
    pnpm install --frozen-lockfile

COPY . .

RUN pnpm exec vite build \
    && touch static/.gitkeep

# --- uv binaries ---
FROM ghcr.io/astral-sh/uv:${UV_VERSION} AS uv

# --- Builder ---
FROM debian:bookworm-slim AS builder

ARG PYTHON_VERSION

# hadolint ignore=DL3008
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY --from=uv /uv /uvx /bin/

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_INSTALL_DIR=/python \
    UV_PYTHON_PREFERENCE=only-managed

RUN uv python install "${PYTHON_VERSION}"

WORKDIR /app

RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project --no-dev

COPY . .

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-dev

COPY --from=frontend /app/static /app/static

ENV DJANGO_SETTINGS_MODULE=config.django.prod

RUN SECRET_KEY=build-only-secret \
    uv run python manage.py collectstatic \
    --noinput \
    --clear \
    --verbosity=2

# --- Django runtime ---
FROM debian:bookworm-slim AS django

LABEL org.opencontainers.image.source="https://github.com/mashrafdev/mahmoudashraf.dev"
LABEL org.opencontainers.image.description="mahmoudashraf.dev Django application"

WORKDIR /app

RUN groupadd --gid 1000 app \
    && useradd \
        --uid 1000 \
        --gid app \
        --shell /bin/bash \
        --create-home app

# hadolint ignore=DL3008
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        ca-certificates \
        libmagickwand-6.q16-6 \
    && rm -rf /var/lib/apt/lists/*

COPY --from=frontend-prod-deps /usr/local/bin/node /usr/local/bin/node
COPY --from=frontend-prod-deps /usr/local/lib/node_modules /usr/local/lib/node_modules
COPY --from=builder /python /python
COPY --from=builder /app /app
COPY --from=frontend-prod-deps /app/node_modules /app/node_modules

ENV PATH="/app/.venv/bin:$PATH" \
    DJANGO_SETTINGS_MODULE=config.django.prod \
    PYTHONDONTWRITEBYTECODE=1

RUN chmod +x /app/bin/django-entrypoint.sh \
    && node --version \
    && python --version \
    && node src/base/blocks/shiki.mjs 'print("ok")' python github-dark >/dev/null

USER app

EXPOSE 8000

ENTRYPOINT ["/app/bin/django-entrypoint.sh"]

# --- Nginx (static files) ---
FROM nginx:${NGINX_VERSION}-alpine AS nginx

LABEL org.opencontainers.image.source="https://github.com/mashrafdev/mahmoudashraf.dev"
LABEL org.opencontainers.image.description="mahmoudashraf.dev static file server"

COPY --from=builder /app/staticfiles /usr/share/nginx/html/static
COPY nginx/site.conf /etc/nginx/nginx.conf
