FROM node:24.14.0-slim AS frontend-base
ENV PNPM_HOME="/pnpm"
ENV PATH="$PNPM_HOME:$PATH"
RUN corepack enable && corepack prepare pnpm@11.7.0 --activate
WORKDIR /app

FROM frontend-base AS frontend-prod-deps
COPY package.json pnpm-lock.yaml ./
RUN --mount=type=cache,id=pnpm,target=/pnpm/store pnpm install --prod --frozen-lockfile

FROM frontend-base AS frontend
COPY package.json pnpm-lock.yaml ./
RUN --mount=type=cache,id=pnpm,target=/pnpm/store pnpm install --frozen-lockfile
COPY . .
RUN pnpm exec vite build && touch static/.gitkeep

FROM ghcr.io/astral-sh/uv:bookworm-slim AS builder

ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy
ENV UV_PYTHON_INSTALL_DIR=/python
ENV UV_PYTHON_PREFERENCE=only-managed

RUN uv python install 3.14.3

WORKDIR /app

RUN --mount=type=cache,target=/root/.cache/uv \
  --mount=type=bind,source=uv.lock,target=uv.lock \
  --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
  uv sync --locked --no-install-project --no-dev

COPY . /app
RUN --mount=type=cache,target=/root/.cache/uv \
  uv sync --locked --no-dev

COPY --from=frontend /app/static /app/static

ENV DJANGO_SETTINGS_MODULE=config.django.prod

RUN SECRET_KEY=build-only-secret uv run python manage.py collectstatic --noinput --clear --verbosity 2

FROM debian:bookworm-slim AS django
LABEL org.opencontainers.image.source="https://github.com/mashrafdev/mahmoudashraf.dev"
LABEL org.opencontainers.image.description="mahmoudashraf.dev Django application"

WORKDIR /app

RUN groupadd --gid 1000 app \
  && useradd --uid 1000 --gid app --shell /bin/bash --create-home app

RUN apt-get update && apt-get install -y --no-install-recommends \
  libmagickwand-dev \
  ca-certificates \
  && update-ca-certificates \
  && rm -rf /var/lib/apt/lists/*

# Node.js for runtime
COPY --from=frontend-prod-deps /usr/local/bin/node /usr/local/bin/node
COPY --from=frontend-prod-deps /usr/local/lib/node_modules /usr/local/lib/node_modules

COPY --from=builder --chown=app:app /python /python
COPY --from=builder --chown=app:app /app /app
COPY --from=frontend-prod-deps --chown=app:app /app/node_modules /app/node_modules
RUN chmod +x /app/bin/django-entrypoint.sh

USER app

ENV PATH="/app/.venv/bin:$PATH"
ENV DJANGO_SETTINGS_MODULE=config.django.prod

EXPOSE 8000
ENTRYPOINT []

FROM docker.io/nginx:1.29.5-alpine AS nginx
LABEL org.opencontainers.image.source="https://github.com/mashrafdev/mahmoudashraf.dev"
LABEL org.opencontainers.image.description="mahmoudashraf.dev nginx reverse proxy"

COPY --from=builder /app/staticfiles /usr/share/nginx/html/static
COPY nginx/site.conf /etc/nginx/nginx.conf
