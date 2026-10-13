# Built from the repository root (see docker-compose.prod.yml), so the frontend is in the context.

# ---- Stage 1: build the single-page app ----
FROM node:26.11.1-alpine AS frontend

WORKDIR /frontend

COPY frontend/package.json frontend/package-lock.json ./
RUN --mount=type=cache,target=/root/.npm npm ci --no-audit --no-fund

COPY frontend ./
RUN npm run build

# ---- Stage 2: nginx serves the app and proxies everything else to Django ----
FROM nginx:1.30.5-alpine

COPY nginx/nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=frontend /frontend/dist /usr/share/nginx/app
