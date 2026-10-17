# Security Policy

## Supported Versions

Only the latest release and the `master` branch receive security fixes. `master` is what runs in production.

## Reporting a Vulnerability

Please **do not** open a public issue for security problems.

Report privately through GitHub: **Security → Report a vulnerability**
(<https://github.com/mehroj-r/url-shortener/security/advisories/new>).

Include what you found, how to reproduce it, and the impact you expect. You should get a reply within a few days;
once a fix is released, the advisory is published with credit unless you prefer otherwise.

Particularly relevant areas: JWT authentication (the refresh token kept in the browser's `localStorage`, and its
blacklisting on logout), invite tokens and invite-only sign-up, per-user access to links, collections, tags and
clicks, short code validation and reservation (codes must never shadow `/admin/`, `/api/` or `/app/`, or be reused
after deletion), the redirect view and the targets it accepts, client IP detection behind the reverse proxy
(`X-Forwarded-For` and `TRUSTED_PROXY_NETWORKS`), login rate limiting, the visitor data stored with each click (IP
address, user agent, referrer), the Django admin, and the production settings (`SECRET_KEY`, `ALLOWED_HOSTS`,
`CORS_ALLOWED_ORIGINS`).
