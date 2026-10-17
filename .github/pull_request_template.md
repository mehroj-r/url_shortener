## Summary

<!-- What does this change and why? Link related issues, e.g. "Closes #12". -->

## Checklist

- [ ] Backend: `uv run ruff check src tests`, the `makemigrations --check` step and `uv run pytest` pass
- [ ] Frontend: `npm run lint`, `npm run typecheck`, `npm test` and `npx vite build` pass
- [ ] Tests added or updated for behaviour changes
- [ ] Migration added for model changes
- [ ] README / `.env.example` updated for new settings
- [ ] Server-side steps listed above, since merging deploys to production
