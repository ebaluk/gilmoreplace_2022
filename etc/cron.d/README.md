# Legacy bare-metal cron (not used on Docker DEV/prod)

These files targeted a host venv (`/home/django/envs/wagtail`) and user `django`.
Server deploy uses Compose service **`backend-cron`** instead
(`deploy/cron/run-scheduled.sh` → `python manage.py publish_scheduled`).

Do not install these into `/etc/cron.d/` on the nginx-proxy VM.
