# Gilmore Place — Agent Instructions

Real-estate marketing site for Gilmore Place (Onni). Wagtail/Django serves content via a headless API; the public frontend lives in `gilmoreplace-next/` (Next.js 14 App Router).

## Язык общения

**Всегда отвечай на русском языке.** Исключения: код, имена файлов, команды терминала, цитаты из кодовой базы и технические идентификаторы — оставляй как есть.

## Project layout

| Path | Purpose |
|------|---------|
| `gilmoreplace_2022/` | Django project settings, headless API (`api/`) |
| `wtpages/`, `wthomepage/`, `towers/`, etc. | Wagtail apps, page models, stream-field blocks |
| `gilmoreplace-next/` | Next.js frontend consuming `/api/v2/headless/` |

## Commands

### Backend (repo root)

```bash
python manage.py runserver          # Django + Wagtail admin (port 8000)
python manage.py test gilmoreplace_2022.api.tests
```

### Frontend (`gilmoreplace-next/`)

```bash
npm run dev       # Next.js dev server (port 3000)
npm run build     # production build
npm run lint      # ESLint
npm run test      # Vitest
```

Set `WAGTAIL_API_URL` when the API is not at `http://localhost:8000/api/v2`.

## Internationalization

Supported locales (keep in sync across backend and frontend):

| Next.js path | Wagtail URL prefix | API locale | Label |
|--------------|-------------------|------------|-------|
| `/en/` | `/en/` | `en-us` | EN |
| `/sc/` | `/sc/` | `zh-hans` | 简 |
| `/tc/` | `/tc/` | `zh-hant` | 繁 |

**When adding or changing a locale**, update all of:

- `gilmoreplace_2022/settings/base.py` — `LANGUAGES`, `LANGUAGES_TRANSLATIONS`
- `gilmoreplace-next/lib/i18n/config.ts` — `locales`, `localeLabels`
- `gilmoreplace-next/lib/urls.ts` — `WAGTAIL_PREFIX_TO_LOCALE`
- `gilmoreplace-next/lib/api/client.ts` — `LOCALE_MAP`
- `gilmoreplace-next/next.config.js` — redirects for legacy Wagtail prefixes (if any)
- `wthomepage` migration for `LanguageRootPage.language_code` choices (when adding a new language)

Wagtail content is localized via `LanguageRootPage` instances (one per language). The Next.js app maps Wagtail URL prefixes to Next locale segments via `wagtailUrlToNextPath()`.

Tower/penthouse type titles only have Chinese overrides (`title_zh_hans`, `title_zh_hant`); other locales fall back to the English `title`.

## Data fetching (TanStack Query)

- **Transport layer**: [`gilmoreplace-next/lib/api/client.ts`](gilmoreplace-next/lib/api/client.ts) — raw `fetch` functions and types.
- **Query keys**: [`gilmoreplace-next/lib/api/query-keys.ts`](gilmoreplace-next/lib/api/query-keys.ts)
- **Query options**: [`gilmoreplace-next/lib/api/queries.ts`](gilmoreplace-next/lib/api/queries.ts) — use `queryOptions()` factories; `staleTime: 60_000` matches ISR.
- **SSR pattern**: Server page calls `prefetchPageData()` → `dehydrate()` → `HydrationBoundary` → client `PageContent` uses `useQuery` with the same options.
- **Client mutations**: form submit via `useMutation` in `FormBlock`; see [`lib/api/form-submit.ts`](gilmoreplace-next/lib/api/form-submit.ts).
- **Tests**: wrap client components with `renderWithQuery()` from [`lib/test-utils.tsx`](gilmoreplace-next/lib/test-utils.tsx).

## Conventions

- **Scope**: Make minimal, focused diffs. Match existing patterns in the file you edit.
- **Frontend**: Functional React components, Tailwind + legacy Bootstrap/site CSS. Stream-field blocks live in `gilmoreplace-next/components/blocks/` and are wired in `StreamFieldRenderer.tsx`.
- **API**: Headless endpoints in `gilmoreplace_2022/api/views.py`; serializers in `serializers.py`. Accept `locale` query param (default `en-us`).
- **Tests**: Run relevant Vitest or Django tests after changes. Do not add trivial tests.
- **Commits**: Only commit when explicitly asked.

## Environment

- Python 3.10, Django 3.2, Wagtail 2.15
- Node 20+ for Next.js
- PostgreSQL in production; local dev may use SQLite or Postgres depending on settings
