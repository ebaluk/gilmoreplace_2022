# Production deploy notes (single VM)

This repo ships with Docker Compose configs under `deploy/compose/` for local reference, and a root **`docker-compose.yaml`** for server deploy (with `prod_server.env`).

**Do not confuse env files:**

| File | Role |
|------|------|
| `prod_server.env` | Server deploy (canonical). Not in git / not rsynced. |
| `.env.production` | Local / `deploy/compose/prod.yml` only. Not used by Actions or `docker-compose.yaml`. |

GitHub Actions ([`.github/workflows/ci.yml`](../.github/workflows/ci.yml) — **CI / CD**) runs tests, then on push to `main` (or manual dispatch) deploys with Ansible. Uses secret `DEV_SSH_PRIVATE_KEY` for SSH only; it does not manage app secrets or upload `.env.production`. See [ansible/README.md](../ansible/README.md).

## Server deploy (DEV: gilmoreplace.ebaluk.store)

The DEV server (`155.212.224.19`, user `appuser`) uses:

- **`docker-compose.yaml`** at repo root
- **`prod_server.env`** — secrets and nginx-proxy vars (not in git; copy manually)
- Host **nginx-proxy** + acme-companion for HTTPS (`nginx-proxy-network`)
- **`backend-cron`** — sidecar that runs `python manage.py publish_scheduled` every 5 minutes (`SCHEDULE_INTERVAL_SEC`, default 300) so Wagtail `go_live_at` / `expire_at` take effect. Manual run: `docker exec gilmoreplace-backend-cron python manage.py publish_scheduled`

Legacy host crontabs under `etc/cron.d/` are for bare-metal only; see that directory’s README.

### Host SSL: nginx-proxy + acme-companion (already on DEV)

On the DEV VM these containers are installed **outside** this repo’s Compose stack (shared reverse proxy for multiple apps). Our `nginx` service only joins their Docker network and advertises env vars; it does **not** run Certbot itself.

| Image | Role |
|-------|------|
| [`nginxproxy/nginx-proxy`](https://github.com/nginx-proxy/nginx-proxy) | Reverse proxy: reads `VIRTUAL_HOST` / `VIRTUAL_PORT` from containers on `nginx-proxy-network` and routes HTTPS/HTTP to them |
| [`nginxproxy/acme-companion`](https://github.com/nginx-proxy/acme-companion) | Issues/renews Let’s Encrypt certs for hosts declared via `LETSENCRYPT_*` |

Required network (must already exist; do not create inside this compose file as non-external):

```bash
docker network ls | grep nginx-proxy-network
# expect: nginx-proxy-network
```

Env vars passed into our `nginx` service from `prod_server.env` (see `docker-compose.yaml`):

| Variable | Purpose |
|----------|---------|
| `VIRTUAL_HOST` | Public hostname nginx-proxy should route to this stack (e.g. `gilmoreplace.ebaluk.store`) |
| `VIRTUAL_PORT` | Container port nginx-proxy connects to (always `80` for our `nginx` service) |
| `LETSENCRYPT_HOST` | Hostname(s) for the certificate — usually same as `VIRTUAL_HOST` |
| `LETSENCRYPT_EMAIL` | Contact email for Let’s Encrypt registration / expiry notices |

DNS for `VIRTUAL_HOST` / `LETSENCRYPT_HOST` must point at the DEV server before acme-companion can obtain a cert. After first successful issue, renewals are handled by acme-companion on the host — no certbot in this project’s compose.

Do **not** use `deploy/compose/prod.ssl.yml` on this VM (built-in certbot overlay); SSL is already provided by the host proxy pair above.

### One-time server setup

1. Ensure Docker + Compose plugin and external network exist:
   ```bash
   docker network ls | grep nginx-proxy-network
   ```
2. Copy env with secrets (rsync/Ansible **do not** sync `prod_server.env`):
   ```bash
   scp -i ~/.ssh/id_beget_ebaluksf prod_server.env appuser@155.212.224.19:/home/appuser/gilmoreplace_2022/
   ```
   Or bootstrap placeholder from example (then edit secrets on server):
   ```bash
   ansible-playbook deploy.yml -e "filevar=dev" --tags=bootstrap
   ```

   In `prod_server.env`, set **`NEXTJS_PUBLIC_URL=https://gilmoreplace.ebaluk.store`** (browser / Wagtail preview) and keep **`NEXTJS_BASE_URL=http://frontend:3000`** (Docker revalidate only). Do not put the Docker hostname in `NEXTJS_PUBLIC_URL`. Confirm `VIRTUAL_HOST`, `LETSENCRYPT_HOST`, and `LETSENCRYPT_EMAIL` match the public domain and a valid contact email.
3. `mkdir -p media_files static` on server (Ansible deploy task also creates them)

### Ansible deploy (from repo `ansible/`)

```bash
ansible-galaxy collection install -r requirements.yml
ansible-playbook deploy.yml -e "filevar=dev" --tags=dev
```

Tags: `sync` (rsync only), `compose` (docker compose up --build), `bootstrap` (copy `prod_server.env.example` if missing).

### Verify

```bash
curl -I https://gilmoreplace.ebaluk.store/en
```

## Compose files location

- **`docker-compose.yaml`**: server deploy (nginx-proxy, `prod_server.env`)
- `deploy/compose/prod.yml`: legacy/reference (direct :80, `.env.production`)
- `deploy/compose/prod.ssl.yml`: HTTPS overlay with built-in certbot (not used on DEV nginx-proxy host)
- `deploy/compose/dev.yml`: local dev (backend :8000, frontend :3000)

## Persistent data

- `./media_files/`: Wagtail uploaded media (must be persistent + backed up)
- `./static/`: Django collected static (can be rebuilt, but keep mounted)
- Database: PostgreSQL volume `postgres_data`

## Backup (recommended)

- Database dump (daily) + retention
- `media_files/` snapshot/rsync (daily) + retention

## First boot (local / without Ansible)

1. Create `prod_server.env` from `prod_server.env.example`
2. `mkdir -p media_files static`
3. `docker compose up -d --build`

Backend container runs `migrate` + `collectstatic` automatically in `entrypoint.sh`.

## Database init from SQL dump (first boot only)

Postgres executes scripts from `deploy/db/initdb.d/` only when its data directory is empty.

- Plain SQL dump at `deploy/db/dump.sql` (restored via `deploy/db/initdb.d/01-restore.sh`)
- To re-run restore: remove the postgres volume and start again

## Local Python deps (uv)

- Install deps: `uv sync`
- Update lockfile: `uv lock`

