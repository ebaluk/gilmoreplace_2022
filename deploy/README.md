# Production deploy notes (single VM)

This repo ships with Docker Compose configs under `deploy/compose/` for local reference, and a root **`docker-compose.yaml`** for server deploy (with `prod_server.env`).

## Server deploy (DEV: gilmoreplace.ebaluk.store)

The DEV server (`155.212.224.19`, user `appuser`) uses:

- **`docker-compose.yaml`** at repo root
- **`prod_server.env`** — secrets and nginx-proxy vars (not in git; copy manually)
- Host **nginx-proxy** + acme-companion for HTTPS (`nginx-proxy-network`)

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

