#!/bin/sh
set -e

echo "==> Running migrations..."
python manage.py migrate --noinput

echo "==> Collecting static files..."
python manage.py collectstatic --noinput --ignore='*.scss'

echo "==> Compressing assets..."
python manage.py compress --force 2>/dev/null || true

echo "==> Starting server..."
exec "$@"
