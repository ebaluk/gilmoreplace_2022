#!/bin/sh
set -e

# Optionally skip migrate on extra replicas (set RUN_MIGRATIONS=0).
# When enabled, use a Postgres advisory lock so concurrent starts do not race.
run_migrations() {
  echo "==> Running migrations..."
  python <<'PY'
import os
import django

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    os.environ.get("DJANGO_SETTINGS_MODULE", "gilmoreplace_2022.settings.production"),
)
django.setup()

from django.core.management import call_command
from django.db import connection

LOCK_KEY = 8675309
engine = connection.settings_dict.get("ENGINE", "")
if "postgresql" in engine:
    with connection.cursor() as cursor:
        cursor.execute("SELECT pg_advisory_lock(%s)", [LOCK_KEY])
    try:
        call_command("migrate", interactive=False)
    finally:
        with connection.cursor() as cursor:
            cursor.execute("SELECT pg_advisory_unlock(%s)", [LOCK_KEY])
else:
    call_command("migrate", interactive=False)
PY
}

if [ "$(id -u)" = "0" ]; then
  mkdir -p /app/log /app/media_files /app/static
  chown -R app:app /app/log /app/media_files /app/static || true
fi

if [ "${RUN_MIGRATIONS:-1}" = "1" ]; then
  run_migrations
else
  echo "==> Skipping migrations (RUN_MIGRATIONS=${RUN_MIGRATIONS})"
fi

echo "==> Collecting static files..."
python manage.py collectstatic --noinput --ignore='*.scss'

echo "==> Starting server..."
if [ "$(id -u)" = "0" ]; then
  # Preserve PATH / VIRTUAL_ENV / Django env so gunicorn finds the venv.
  exec runuser -u app --preserve-environment -- "$@"
fi
exec "$@"
