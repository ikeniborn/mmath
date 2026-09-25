# Deployment: external Traefik and external PostgreSQL

The project ships two containers, `api` and `web` (Caddy serving the SPA and proxying `/api` to the API), plus a one-shot `migrate` job. It does not deploy TLS termination or a database: an operator-managed Traefik terminates TLS and routes the public host to the edge container, and an operator-managed PostgreSQL holds all data. No database or API port is published in public mode.

## Prerequisites

- Docker with Compose v2 on the edge host. On the minipc host the project lives at `/opt/minipc-traefik/mmath/` next to the other services; the real `.env` stays only there with mode `600`, the tracked `deploy/.env.example` carries placeholders only.
- A database and role on the platform PostgreSQL 18 (`framework` host, LAN `192.168.68.123:5432`, no TLS by owner decision, so the DSN is LAN-only). Role bootstrap on that platform does not create application databases: ask the platform owner for role `mmath` (LOGIN, non-privileged) owning database `mmath`, then set `MMATH_DATABASE_URL`. `host.docker.internal` is only for a database on the docker host itself.
- Public mode: the external Traefik (file provider only, the docker provider is disabled) on network `proxy-net` with entrypoint `websecure` and certificate resolver `letsencrypt`; the DNS record `mmath.ikeniborn.ru` → the edge host. Exposure is a human decision: do not add the DNS record or copy the route before the release checklist is signed off.

## Public mode

```bash
cp deploy/.env.example .env
# edit .env: MMATH_DATABASE_URL, MMATH_MODE=public, MMATH_ORIGIN=https://<host>, TRAEFIK_NETWORK, MMATH_EDGE_ALIAS
docker compose --env-file .env -f compose.yaml -f deploy/compose.public.yaml config --quiet
docker compose --env-file .env -f compose.yaml -f deploy/compose.public.yaml up -d --build --wait
```

Then copy the tracked route `deploy/traefik/conf.d/mmath.yml` to `/opt/minipc-traefik/conf.d/mmath.yml` (back up any previous copy first; the file provider reloads automatically). Its router `mmath-web` uses the exact rule ``Host(`mmath.ikeniborn.ru`)``, entrypoint `websecure`, resolver `letsencrypt` and service `http://mmath-web:80`, so `MMATH_EDGE_ALIAS` must stay `mmath-web`. The contract test in `backend/tests/integration/test_deployment_security.py` asserts these values; change them together. The API listens only inside the compose network and trusts forwarded headers only from the edge.

## LAN HTTP mode

```bash
# .env: MMATH_MODE=lan-http, MMATH_ORIGIN=http://<lan-address>:<port>, MMATH_LAN_BIND=<lan-address>, MMATH_LAN_PORT=<port>
docker compose --env-file .env -f compose.yaml -f deploy/compose.lan-http.yaml up -d --build --wait
```

LAN HTTP is an explicit choice, never a fallback: credentials and content are visible to anyone on the network segment. Bind to a LAN address, never to a WAN interface, and prefer `127.0.0.1` for a single-machine setup.

## Migrations, health and restart

`migrate` runs `alembic upgrade head` once before the API starts; the API refuses to become healthy until `GET /health/ready` reports the database reachable and the schema at the current revision. `/health/*` and `/internal/metrics` are reachable only inside the compose network (the edge does not route them). A migration failure leaves the previous containers stopped and the database untouched; fix and re-run `up`. `docker compose ... down` without `--volumes` keeps all data because the data lives in the external database.

## Verification without touching a real deployment

```bash
uv run --project backend python scripts/check_deployment.py
uv run --project backend python scripts/check_deployment.py --isolated
uv run --project backend python scripts/check_assets.py
```

The isolated run creates a uniquely named compose project against the disposable test PostgreSQL, registers a synthetic account, restarts only the API, confirms the session survived and removes only what it created.

## Recovery and limits

Password recovery is operator-assisted (see `account-recovery.md`); email ownership is not verified (design finding F-001). The external Traefik owns certificates and access logs; the API logs JSON lines with secret fields redacted and exposes aggregate counters only.
