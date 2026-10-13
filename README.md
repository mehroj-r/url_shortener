# URL Shortener

Django REST API for short links: users group URLs into collections, create short codes for them, and see click analytics. Visiting `https://url.mekhroj.com/<code>` redirects to the target and records the click.

Stack: Python 3.14, Django 6.1, Django REST Framework, SimpleJWT, PostgreSQL 17, gunicorn behind nginx, managed with [uv](https://docs.astral.sh/uv/).

## Local development

```sh
cp .env.example .env      # set DEBUG=True and a POSTGRES_PASSWORD
docker compose up --build # API on http://127.0.0.1:8005, Postgres on 127.0.0.1:5400
docker compose exec web python manage.py migrate
```

Or without Docker for the app (Postgres from compose):

```sh
uv sync
cd src && uv run python manage.py runserver   # with POSTGRES_HOST=localhost, POSTGRES_PORT=5400 in .env
```

## Tests and lint

The tests need a Postgres the test runner can create a database on (the compose one works):

```sh
POSTGRES_HOST=localhost POSTGRES_PORT=5400 uv run pytest
uv run ruff check src tests
```

## API overview

All under `/api/v1/`:

| Path | |
|---|---|
| `auth/register/`, `auth/login/`, `auth/logout/`, `auth/token-refresh/`, `auth/token-verify/` | JWT auth (rate limited per IP) |
| `shortener/url-collections/`, `shortener/url-collections/{id}/urls/` | Collections and the URLs in them |
| `shortener/urls/`, `shortener/urls/{id}/short-urls/` | URLs and their short codes |
| `shortener/short-urls/` | Short codes; omit `short_url` to get a random 7-character code |
| `analytics/url-clicks/?short_url_id=&url_id=` | Clicks on your links |

Short codes may use letters, digits, `-` and `_`. Codes are never reused, even after deletion, so old shared links can't be taken over.

## Deployment

Every push to `master` runs lint and tests, bumps the patch version in `pyproject.toml`, then deploys over SSH:
`git pull` on the server followed by `docker compose -f docker-compose.prod.yml up -d --build`.
Migrations and `collectstatic` run when the web container starts.

Repository secrets: `SSH_HOST`, `SSH_USERNAME`, `SSH_PRIVATE_KEY`.

The server's `.env` must define every variable in `.env.example`; production refuses to start without `SECRET_KEY`.

## Backups

`scripts/backup.sh` dumps the production database to `./backups` (gzip, 14 days kept). Run it from cron on the host:

```cron
0 3 * * * cd /path/to/url_shortener && ./scripts/backup.sh >> backups/backup.log 2>&1
```

The restore command is in the script's header.
