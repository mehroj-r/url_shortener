# Contributing

Thanks for your interest! Bug reports, ideas and pull requests are welcome.

## Getting Started

```bash
cp .env.example .env      # set DEBUG=True and a POSTGRES_PASSWORD
docker compose up --build # API on http://127.0.0.1:8005, app on http://127.0.0.1:5173/app/
docker compose exec web python manage.py migrate
docker compose exec web python manage.py createsuperuser
```

To run the frontend on the host instead, see the [README](README.md#local-development).

## Before Opening a Pull Request

These are the checks CI runs:

```bash
cd backend
uv run ruff check src tests
DJANGO_SETTINGS_MODULE=config.settings.test uv run python src/manage.py makemigrations --check --dry-run
POSTGRES_HOST=localhost POSTGRES_PORT=5400 uv run pytest   # needs a Postgres it can create a database on

cd ../frontend
npm run lint && npm run typecheck && npm test && npx vite build
```

- Keep changes focused; one topic per pull request.
- Add or update tests when behaviour changes: `backend/tests/` for the API, `*.test.ts(x)` next to the code in
  `frontend/src/`.
- Model changes need a migration (`uv run python src/manage.py makemigrations`).
- New settings go in `.env.example`, with a comment when the name doesn't explain itself.
- For frontend changes, follow [`DESIGN.md`](DESIGN.md) and [`PRODUCT.md`](PRODUCT.md).
- Commit messages follow [Conventional Commits](https://www.conventionalcommits.org/) (`feat(api): ...`,
  `fix: ...`, `docs: ...`).
- Pull requests target `master` and are squash-merged. Merging deploys to production, so list any steps the server
  needs (new environment variables, a manual migration) in the pull request.

## Questions and Security

Ask questions in [Discussions](https://github.com/mehroj-r/url-shortener/discussions). Report vulnerabilities
privately as described in [`SECURITY.md`](SECURITY.md).

By participating you agree to follow the [Code of Conduct](CODE_OF_CONDUCT.md).
