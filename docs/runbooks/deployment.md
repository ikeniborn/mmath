# Deployment: external Traefik and external PostgreSQL

The project ships two containers, `api` and `web` (Caddy serving the SPA and proxying `/api` to the API), plus a one-shot `migrate` job. It does not deploy TLS termination or a database: an operator-managed Traefik terminates TLS and routes the public host to the edge container, and an operator-managed PostgreSQL holds all data. No database or API port is published in public mode.

## Prerequisites

- Docker with Compose v2 on the edge host. On the minipc host the project lives at `/opt/minipc-traefik/mmath/` next to the other services; the real `.env` stays only there with mode `600`, the tracked `deploy/.env.example` carries placeholders only.
- A database and role on the platform PostgreSQL 18 (`framework` host, LAN `192.168.68.123:5432`, no TLS by owner decision, so the DSN is LAN-only). Role bootstrap on that platform does not create application databases: ask the platform owner for role `mmath` (LOGIN, non-privileged) owning database `mmath`, then set `MMATH_DATABASE_URL`. Percent-encode reserved characters in the password (`@` → `%40`, `/` → `%2F`, `#` → `%23`); SQLAlchemy and the migrations accept the encoded form. `host.docker.internal` is only for a database on the docker host itself.
- Public mode: the external Traefik (file provider only, the docker provider is disabled) on network `proxy-net` with entrypoint `websecure` and certificate resolver `letsencrypt`; the DNS record `mmath.ikeniborn.ru` → the edge host. Exposure is a human decision: do not add the DNS record or copy the route before the release checklist is signed off.

## Public mode

```bash
cp deploy/.env.example .env
# edit .env: MMATH_DATABASE_URL, MMATH_MODE=public, MMATH_ORIGIN=https://<host>, TRAEFIK_NETWORK, MMATH_EDGE_ALIAS, MMATH_TRUSTED_PROXIES
docker compose --env-file .env -f compose.yaml -f deploy/compose.public.yaml config --quiet
docker compose --env-file .env -f compose.yaml -f deploy/compose.public.yaml up -d --build --wait
```

Then copy the tracked route `deploy/traefik/conf.d/mmath.yml` to `/opt/minipc-traefik/conf.d/mmath.yml` (back up any previous copy first; the file provider reloads automatically). Its router `mmath-web` uses the exact rule ``Host(`mmath.ikeniborn.ru`)``, entrypoint `websecure`, resolver `letsencrypt` and service `http://mmath-web:80`, so `MMATH_EDGE_ALIAS` must stay `mmath-web`. The contract test in `backend/tests/integration/test_deployment_security.py` asserts these values; change them together. The API listens only inside the compose network and trusts forwarded headers only from the edge. The edge (Caddy) in turn trusts `X-Forwarded-For` only from `MMATH_TRUSTED_PROXIES`, the CIDR of the Traefik network (`docker network inspect proxy-net --format '{{range .IPAM.Config}}{{.Subnet}}{{end}}'`); without it every internet client would share Traefik's address and the per-address sign-in throttle would degrade to per-account, letting anyone lock a parent out. Verify after the first public start: sign in from one device, watch the API log's `request` lines, and confirm `login_throttled` does not fire for a second device after five failures on the first.

## LAN HTTP mode

```bash
# .env: MMATH_MODE=lan-http, MMATH_ORIGIN=http://<lan-address>:<port>, MMATH_LAN_BIND=<lan-address>, MMATH_LAN_PORT=<port>
docker compose --env-file .env -f compose.yaml -f deploy/compose.lan-http.yaml up -d --build --wait
```

LAN HTTP is an explicit choice, never a fallback: credentials and content are visible to anyone on the network segment. Bind to a LAN address, never to a WAN interface, and prefer `127.0.0.1` for a single-machine setup.

## Host placement on minipc

Services on `minipc` live under `/opt/<service>`; mmath is `/opt/mmath`. The directory holds the source checkout the images are built from and the only copy of the runtime configuration:

- `/opt/mmath/src` — git checkout of the deployed revision (`git -C /opt/mmath/src pull` to update, then rebuild).
- `/opt/mmath/.env` — mode `600`, owner `ikeniborn`, outside the checkout; the DSN password lives only here. The tracked `deploy/.env.example` carries the placeholders.
- Compose project name `mmath`; `deploy/minipc-lan.sh` wraps every compose command with this env file and the checkout as project directory (`up|ps|logs|down|config`). The host ships the standalone Compose v2 binary `docker-compose` (no `docker compose` plugin); the wrapper picks whichever exists, so the `docker compose ...` lines elsewhere in this runbook read as `docker-compose ...` on minipc.

LAN deployment on this host (no public domain): `MMATH_MODE=lan-http`, `MMATH_ORIGIN=http://192.168.68.135:8080`, `MMATH_LAN_BIND=192.168.68.135`, `MMATH_LAN_PORT=8080` (port 80 belongs to the platform Traefik).

Database access follows the platform's generated `pg_hba.conf` (never edited by hand): LAN clients match `host all +external_login 192.168.68.0/24 scram-sha-256`, so the application role must be a member of `external_login`, non-privileged and LOGIN. Run once on the framework host as the platform superuser:

```sql
ALTER ROLE mmath NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS LOGIN;
GRANT external_login TO mmath;
```

A probe from minipc with a wrong password must answer `password authentication failed`; `pg_hba.conf rejects connection ... no encryption` means the membership is missing. Passwords go into the DSN percent-encoded, or better contain only letters and digits: an unencoded `@` splits the URL and the migration job logs the fragment after it as an unresolvable host name.

First LAN start on 2026-09-25: migrations applied, `/health/ready` answered `database ok, schema ok` inside the network, the edge served the SPA and `/api/v1/auth/session` while hiding `/health/*` and `/internal/*`, and a synthetic parent registered a child, played one addition task, finished the session and read the progress page through `http://192.168.68.135:8080`.

Early numeracy deployment on 2026-09-26 (branch dev-early-numeracy-game-tasks, 1a004a8): migration 0010 applied, readiness ok, a synthetic age-4 profile played two six-task rounds through the edge with the early kinds and answer cards and earned two stickers, an age-7 profile kept ten tasks without cards; `POST /api/v1/sessions` p95 16 ms over 23 starts (target ≤ 60 ms), served bundle 107.8 KB JS + 2.8 KB CSS gzip (budget 160 KB), no API or edge errors. Synthetic accounts `lan-early-<timestamp>@example.com` remain in the database.

```bash
/opt/mmath/src/deploy/minipc-lan.sh config
/opt/mmath/src/deploy/minipc-lan.sh up
/opt/mmath/src/deploy/minipc-lan.sh ps
```

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
