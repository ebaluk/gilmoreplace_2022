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
| `requirements.yml` | Galaxy collections (`community.docker`, `ansible.posix`) |
| `logs/` | Ansible run log (gitignored except `.gitkeep`) |

## GitHub Actions (CI / CD)

Workflow: [`.github/workflows/ci.yml`](../.github/workflows/ci.yml) (`CI / CD`)

| Job | When |
|-----|------|
| `backend` / `frontend` | Every push, PR, and manual run |
| `deploy` | After green tests on **push to main/master** or **workflow_dispatch** (not on PR) |

Manual run: Actions → **CI / CD** → Run workflow → choose Ansible tags (`dev` / `sync` / `compose` / `bootstrap`).

Required GitHub configuration:

1. Repository secret **`DEV_SSH_PRIVATE_KEY`** — full PEM for `appuser@155.212.224.19` (same key as `~/.ssh/id_beget_ebaluksf` locally). Repository secrets are enough; no need to duplicate under Environment secrets.
2. Environment **`dev`** — used by the deploy job (optional protection / reviewers).

App secrets stay on the server in **`prod_server.env`** (not synced by rsync; not written by Actions). Do **not** store `.env.production` or `SECRET_KEY` / DB passwords as GitHub Secrets — only SSH is needed.

Compose brings up **`backend-cron`** with the stack (Wagtail `publish_scheduled` every 5 minutes). No host cron install required.

### Diagnosing a failed Actions deploy

| Failed step | Likely cause |
|-------------|--------------|
| Configure SSH key / Missing secret | Secret name typo (should be `DEV_SSH_PRIVATE_KEY`) |
| SSH smoke-test — `Permission denied (publickey)` | Wrong key contents / newlines in the secret |
| SSH smoke-test — timeout / no route | Firewall: allow SSH from GitHub Actions IPs to `155.212.224.19:22` |
| Deploy with Ansible (after green smoke-test) | Compose/build on server — check Ansible task output |
| `couldn't resolve module ... synchronize` | Collections not installed — workflow runs `ansible-galaxy collection install -r requirements.yml` (`ansible.posix`) |

Local deploy still works without Actions:

```bash
cd ansible
ansible-playbook deploy.yml -e "filevar=dev" --tags=dev
```

## Prerequisites

- Ansible 2.14+ on your machine
- SSH key: set `ANSIBLE_PRIVATE_KEY_FILE` or use default `~/.ssh/id_beget_ebaluksf` (see `vars_dev.yml`)
- Docker + Compose plugin on the remote host
- External Docker network `nginx-proxy-network` on the server ([`nginxproxy/nginx-proxy`](https://github.com/nginx-proxy/nginx-proxy) + [`nginxproxy/acme-companion`](https://github.com/nginx-proxy/acme-companion) already installed on DEV — see [deploy/README.md](../deploy/README.md#host-ssl-nginx-proxy--acme-companion-already-on-dev))
- In `prod_server.env`: `VIRTUAL_HOST`, `VIRTUAL_PORT`, `LETSENCRYPT_HOST`, `LETSENCRYPT_EMAIL`

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
