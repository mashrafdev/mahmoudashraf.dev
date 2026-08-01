#!/usr/bin/env bash

set -euo pipefail

python manage.py migrate --noinput

exec gunicorn config.wsgi \
  --workers "${WEB_CONCURRENCY:-3}" \
  --bind 0.0.0.0:8000 \
  --worker-class gthread \
  --threads 4 \
  --timeout 60 \
  --access-logfile - \
  --error-logfile - \
  --log-level info \
  --max-requests 1000 \
  --log-config-json logconfig.json \
  --no-control-socket \
  --max-requests-jitter 100 \
  --forwarded-allow-ips="*"
