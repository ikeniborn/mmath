# Release checklist

Every public release passes these gates; the human checkpoints are signed by a person, not inferred from tests.

## Automated gates (all exit 0)

- `uv run --project backend pytest backend/tests -q`
- `(cd frontend && npm run typecheck && npm run test -- --run && npm run build && npm run test:e2e)`
- `uv run --project backend python scripts/check_contract.py`
- `uv run --project backend python scripts/check_deployment.py --isolated`
- `uv run --project backend python scripts/check_assets.py`
- backup drill from `backup-restore.md` against the disposable database

## Human checkpoints

- Public exposure: DNS record and the Traefik `conf.d` route are added only after explicit authorization; the API origin matches the public host exactly.
- External PostgreSQL: backup schedule agreed, credentials stored outside the repository, `MMATH_DATABASE_URL` never logged or committed.
- Supervised usability review with a younger (5–6) and an older (9–10) child, recording only actionable interface findings and no identifying data. Status: **not yet performed**.
- Device installation review for the PWA (future task): record device and browser versions.
- Known limitation F-001: email is unverified and recovery is operator-assisted; the parent help text states it.
