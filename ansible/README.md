# Ansible deploy

Playbooks for deploying Gilmore Place to the DEV server (`gilmoreplace.ebaluk.store`).

Run all commands from this directory (`ansible/`).

## Layout

| File | Purpose |
|------|---------|
| `deploy.yml` | Sync code + rebuild Docker Compose stack |
| `vars_dev.yml` | DEV host, paths, rsync excludes, compose file |
| `hosts.ini` | Inventory (`dev_hosts`) |
| `ansible.cfg` | Inventory + log path |
| `requirements.yml` | Galaxy collections (`community.docker`) |
| `logs/` | Ansible run log (gitignored except `.gitkeep`) |

## GitHub Actions deploy

Workflow: [`.github/workflows/deploy-dev.yml`](../.github/workflows/deploy-dev.yml)

Triggers:

- **workflow_dispatch** — choose tags (`dev` / `sync` / `compose` / `bootstrap`)
- **push** to `main` / `master` — full `--tags=dev`

Required GitHub configuration:

1. Repository secret **`DEV_SSH_PRIVATE_KEY`** — private key for `appuser@155.212.224.19` (same key as `~/.ssh/id_beget_ebaluksf` locally).
2. Environment **`dev`** (optional protection rules / reviewers).

`prod_server.env` is **not** synced; keep secrets on the server as today.

## Prerequisites

- Ansible 2.14+ on your machine
- SSH key matching `vars_dev.yml` / `hosts.ini` (`~/.ssh/id_beget_ebaluksf`)
- Docker + Compose plugin on the remote host
- External Docker network `nginx-proxy-network` on the server (nginx-proxy + acme-companion)

Install collections once:

```bash
ansible-galaxy collection install -r requirements.yml
```

## First-time server setup

1. Ensure the remote path exists (`deploy_dest` in `vars_dev.yml`, default `/home/appuser/gilmoreplace_2022`).
2. Create secrets file on the server (rsync **never** copies it):

   ```bash
   # Option A: copy a filled env from your machine
   scp -i ~/.ssh/id_beget_ebaluksf ../prod_server.env \
     appuser@155.212.224.19:/home/appuser/gilmoreplace_2022/

   # Option B: bootstrap empty file from example, then edit on server
   ansible-playbook deploy.yml -e "filevar=dev" --tags=bootstrap
   ```

3. Edit `prod_server.env` on the server: secrets, `VIRTUAL_HOST` / SSL vars, `PREVIEW_SECRET`, `REVALIDATION_SECRET`, etc. See `../prod_server.env.example`.

   **Preview URLs (important):** keep these distinct —

   | Variable | Value on DEV | Used for |
   |----------|--------------|----------|
   | `NEXTJS_PUBLIC_URL` | `https://gilmoreplace.ebaluk.store` | Browser / Wagtail admin preview links |
   | `NEXTJS_BASE_URL` | `http://frontend:3000` | Server→Next revalidate only |

   Never set `NEXTJS_PUBLIC_URL` to `http://frontend:3000` — browsers cannot open that host. Ansible does not sync `prod_server.env`; after editing it, recreate backend/frontend:

   ```bash
   docker compose --env-file prod_server.env up -d --force-recreate backend frontend
   ```

## Deploy

Full deploy (rsync + compose down/up --build):

```bash
ansible-playbook deploy.yml -e "filevar=dev" --tags=dev
```

### Tags

| Tag | What it does |
|-----|----------------|
| `dev` | Full path used by the examples below (includes sync + compose) |
| `sync` | Rsync project to the server only |
| `compose` | Tear down stale containers/images, then `docker compose` build/up |
| `bootstrap` | Copy `prod_server.env.example` → `prod_server.env` if missing |
| `deploy` | Shared by sync / compose / bootstrap tasks |

Examples:

```bash
ansible-playbook deploy.yml -e "filevar=dev" --tags=sync
ansible-playbook deploy.yml -e "filevar=dev" --tags=compose
ansible-playbook deploy.yml -e "filevar=dev" --tags=bootstrap
```

`filevar=dev` loads `vars_dev.yml`. Add `vars_prod.yml` (and inventory group) later the same way.

## What gets synced

Source: repo root (`deploy_src`). Destination: `deploy_dest` on the server.

**Excluded** (see `rsync_excludes` in `vars_dev.yml`):

- `.git`, `.venv`, `node_modules`, `gilmoreplace-next/.next`
- `media_files`, `static` (persist on server)
- `prod_server.env`, `.env.local`, `.env.production`
- `ansible/` itself and `ansible/logs`

`delete: false` — files removed locally are **not** deleted on the server by rsync.

## Compose on the server

- Compose file: `docker-compose.yaml` (repo root)
- Env file: `prod_server.env` (must exist on the server)
- Persistent dirs created by the playbook: `media_files/`, `static/`

The compose task force-removes known container names, runs `compose down --rmi local`, then builds and recreates the stack.

## Verify

```bash
curl -I https://gilmoreplace.ebaluk.store/en
```

More server/ops notes: [`../deploy/README.md`](../deploy/README.md).
