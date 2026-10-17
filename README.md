# Spur

[![CI](https://github.com/mehroj-r/url-shortener/actions/workflows/ci.yml/badge.svg)](https://github.com/mehroj-r/url-shortener/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python 3.14](https://img.shields.io/badge/python-3.14-blue.svg)](https://www.python.org/)
[![React 19](https://img.shields.io/badge/react-19-blue.svg)](https://react.dev/)

Spur is a self-hosted, invite-only link shortener with collections, tags, expiring short codes and click analytics, built on Django REST Framework and React. Visiting `https://url.mekhroj.uz/<code>` redirects to the target and records the click; the web app at `https://url.mekhroj.uz/app/` creates and organises links and shows where clicks come from. Only the owner and the people they invite can sign in.

| Directory | What |
|---|---|
| `backend/` | Django 6.1 REST API, Python 3.14, PostgreSQL 18, gunicorn. Managed with [uv](https://docs.astral.sh/uv/). In production it also serves the built frontend and static files (WhiteNoise). |
| `frontend/` | React 19 + Vite + TypeScript single-page app, served under `/app/`. |
| `scripts/` | Host-side operations (database backups). |

`PRODUCT.md` and `DESIGN.md` describe who the product is for and its visual system.

## Local development

```sh
cp .env.example .env      # set DEBUG=True and a POSTGRES_PASSWORD
docker compose up --build # API on http://127.0.0.1:8005, app on http://127.0.0.1:5173/app/
docker compose exec web python manage.py migrate
docker compose exec web python manage.py createsuperuser   # the first account; everyone else joins by invite
```

The frontend dev server proxies `/api` to the Django container. To run it on the host instead:

```sh
cd frontend
npm install
npm run dev            # API_PROXY=http://127.0.0.1:8005 by default
```

## Tests and lint

```sh
cd backend
POSTGRES_HOST=localhost POSTGRES_PORT=5400 uv run pytest   # needs a Postgres it can create a database on
uv run ruff check src tests

cd ../frontend
npm run lint && npm run typecheck && npm test
```

## API overview

All under `/api/v1/`:

| Path | |
|---|---|
| `auth/login/`, `auth/logout/`, `auth/token-refresh/`, `auth/token-verify/` | JWT auth (login rate limited per IP) |
| `auth/register/`, `auth/invites/`, `auth/invites/check/{token}/` | Invite-only sign-up |
| `auth/me/`, `auth/change-password/` | Profile and password |
| `shortener/urls/` | Links: search, filter by collection/tag/status, sort; `POST` creates the link and its first code in one call; `urls/bulk/` for bulk actions |
| `shortener/urls/{id}/short-urls/`, `shortener/short-urls/` | Short codes, with optional expiry |
| `shortener/url-collections/`, `shortener/tags/` | Collections (each with a line colour) and tags |
| `analytics/summary/?days=&url=&collection=&tag=` | Clicks over time, by hour, top links, referrers, browsers, systems and devices |
| `analytics/url-clicks/` | Individual clicks |

Short codes may use letters, digits, `-` and `_`. Codes are never reused, even after deletion, so old shared links can't be taken over. Clicks from link previews and crawlers (Telegram, WhatsApp, Slack…) are recorded but not counted.

## Deployment

Every push to `master` runs the backend and frontend checks, bumps the patch version in `backend/pyproject.toml`, then deploys over SSH:
`git pull` on the server followed by `docker compose -f docker-compose.prod.yml up -d --build`.
The web image builds the frontend into itself (`backend/Dockerfile`, built from the repository root), and migrations and `collectstatic` run when the container starts.
It listens on `127.0.0.1:1050`. The host's reverse proxy terminates TLS and forwards there, and it must send `X-Forwarded-Proto: https` and append the visitor's address to `X-Forwarded-For` (nginx: `proxy_set_header X-Forwarded-Proto $scheme;` and `proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;`).

Repository secrets: `SSH_HOST`, `SSH_USERNAME`, `SSH_PRIVATE_KEY`.

The server's `.env` must define every variable in `.env.example`; production refuses to start without `SECRET_KEY`. Point `DEFAULT_REDIRECT_URL` at `https://url.mekhroj.uz/app/` so unknown codes land on the app.

## Backups

`scripts/backup.sh` dumps the production database to `./backups` (gzip, 14 days kept). Run it from cron on the host:

```cron
0 3 * * * cd /path/to/url_shortener && ./scripts/backup.sh >> backups/backup.log 2>&1
```

The restore command is in the script's header.

## Contributing

Contributions are welcome: see [CONTRIBUTING.md](CONTRIBUTING.md). Please report security issues privately as described in [SECURITY.md](SECURITY.md).

## License

Released under the [MIT License](LICENSE).
