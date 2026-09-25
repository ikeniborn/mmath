#!/bin/sh
# LAN deployment wrapper for the minipc host: the runtime configuration lives in /opt/mmath/.env (mode 600, never in
# the checkout) and the compose project runs from the source checkout. Usage: deploy/minipc-lan.sh up|ps|logs|down|config
set -eu

env_file="${MMATH_ENV_FILE:-/opt/mmath/.env}"
src="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
[ -f "$env_file" ] || { echo "missing $env_file (copy deploy/.env.example, fill it, chmod 600)" >&2; exit 2; }

compose() {
  docker compose --project-directory "$src" --env-file "$env_file" -f "$src/compose.yaml" -f "$src/deploy/compose.lan-http.yaml" "$@"
}

case "${1:-}" in
  up) compose up -d --build --wait ;;
  ps) compose ps ;;
  logs) shift; compose logs "$@" ;;
  down) compose down ;;  # never --volumes: the project owns no data volume, the database is external
  config) compose config --quiet && echo "compose config ok" ;;
  *) echo "usage: $0 up|ps|logs [service]|down|config" >&2; exit 2 ;;
esac
