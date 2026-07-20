#!/bin/sh
# Periodically publish/unpublish Wagtail pages with go_live_at / expire_at.
# Used by the backend-cron Compose service (overrides Django entrypoint).
set -eu
INTERVAL="${SCHEDULE_INTERVAL_SEC:-300}"

echo "==> backend-cron: publish_scheduled every ${INTERVAL}s"
while true; do
  python manage.py publish_scheduled || true
  sleep "$INTERVAL"
done
