# Gilmore Place

Real-estate marketing site for Gilmore Place (Onni). Content is managed in **Wagtail/Django** and served through a headless API; the public site is a **Next.js** App Router frontend.

## Stack

| Layer | Tech |
|-------|------|
| CMS / API | Python 3.12, Django 5.2, Wagtail 7.4, Django REST Framework |
| Frontend | Next.js 14, React 18, TanStack Query, Tailwind + legacy site CSS |
| DB | PostgreSQL (production); local may use SQLite or Postgres |
| Deploy | Docker Compose + Ansible (`ansible/`), nginx-proxy for SSL |

## Project layout

| Path | Purpose |
|------|---------|
| `gilmoreplace_2022/` | Django settings, headless API (`api/`) |
| `wtpages/`, `wthomepage/`, `towers/`, … | Wagtail apps, page models, stream-field blocks |
| `gilmoreplace-next/` | Next.js frontend (`/api/v2/headless/`) |
| `ansible/`, `deploy/` | Deploy playbooks and server notes |
| `docker-compose.yaml` | Server stack (Postgres, backend, frontend, nginx) |

## Local development

### Backend (repo root)

```bash
# System libs (Debian/Ubuntu-style examples; see install.txt)
# python3-dev libjpeg, libxml, libxslt, freetype, etc.

uv sync
source .venv/bin/activate   # or: uv run …

python manage.py migrate
python manage.py runserver  # http://localhost:8000 — Wagtail admin + API
```

API tests:

```bash
python manage.py test gilmoreplace_2022.api.tests
```

### Frontend (`gilmoreplace-next/`)

```bash
cd gilmoreplace-next
cp .env.local.example .env.local   # set WAGTAIL_API_URL if needed
npm install
npm run dev       # http://localhost:3000
npm run build
npm run lint
npm run test      # Vitest
```

Default API base: `http://localhost:8000/api/v2`. Override with `WAGTAIL_API_URL`.

## Headless API

Custom endpoints live under `/api/v2/headless/` (see `gilmoreplace_2022/api_router.py` and `api/views.py`). Wagtail’s built-in v2 API (`pages`, `images`, `documents`) is also registered.

Common routes:

- `GET /api/v2/headless/pages/` — page listing
- `GET /api/v2/headless/pages/by-slug/?slug=…&locale=en-us` — page by slug
- `GET /api/v2/headless/navigation/`, `settings/`, `themes/`, `towers/`, …
- `POST /api/v2/headless/forms/<id>/submit/` — form submit

Locale query param defaults to `en-us`.

OpenAPI / Swagger (drf-spectacular):

- Schema: `/api/schema/`
- UI: `/api/docs/`

Outbound payloads for settings, forms, and page detail are validated with Pydantic models in `gilmoreplace_2022/api/schemas/`.

Admin page preview uses `wagtail-headless-preview` → Next.js Draft Mode (`/api/preview`) and `GET /api/v2/headless/pages/preview/`. There is no Django HTML frontend for public pages.

## Internationalization

| Next.js path | Wagtail prefix | API locale | Label |
|--------------|----------------|------------|-------|
| `/en/` | `/en/` | `en-us` | EN |
| `/sc/` | `/sc/` | `zh-hans` | 简 |
| `/tc/` | `/tc/` | `zh-hant` | 繁 |

Keep locales in sync in settings, Next i18n config, URL maps, and API client (`LOCALE_MAP`). Content is rooted at `LanguageRootPage` per language.

## Data fetching (frontend)

- Transport: `gilmoreplace-next/lib/api/client.ts`
- Query keys / options: `lib/api/query-keys.ts`, `lib/api/queries.ts`
- SSR: `prefetchPageData` → `dehydrate` → `HydrationBoundary` → client `useQuery`
- Forms: `useMutation` via `lib/api/form-submit.ts`

Stream-field blocks: `gilmoreplace-next/components/blocks/`, wired in `StreamFieldRenderer.tsx`.

## Deploy

See [deploy/README.md](deploy/README.md) for server layout and verification.

```bash
cd ansible
ansible-galaxy collection install -r requirements.yml
ansible-playbook deploy.yml -e "filevar=dev" --tags=dev
```

Copy `prod_server.env.example` → `prod_server.env` on the server (secrets are not rsync’d).

## Agent / contributor notes

Cursor agent conventions live in [AGENTS.md](AGENTS.md).
