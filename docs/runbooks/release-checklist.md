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

- Public exposure: DNS record and the Traefik `conf.d` route are added only after explicit authorization; the API origin matches the public host exactly; `MMATH_TRUSTED_PROXIES` equals the Traefik network CIDR and the forwarded-address check in `deployment.md` passed.
- External PostgreSQL: backup schedule agreed, credentials stored outside the repository, `MMATH_DATABASE_URL` never logged or committed.
- Supervised usability review with a younger (5–6) and an older (9–10) child, recording only actionable interface findings and no identifying data. Status: **not yet performed**.
- Device installation review for the PWA per `mobile-installation.md`: Android (Chromium) and iOS (Safari) install, launch, offline launch after sign-out, update banner at a safe screen. Record device model, OS and browser versions here. Status: **not yet performed** (Chromium service-worker and cache behaviour is covered by `frontend/e2e/pwa.spec.ts`).
- Active policy: `MMATH_POLICY_MODE=active` only after the checkpoint in `active-policy-rollout.md` is signed (confidence semantics verified, offline calibration reviewed, rollout decision recorded in the task ledger). Status: **not authorized**; shadow evidence is the prerequisite.
- Picture mode: `uv run --project backend python scripts/check_assets.py` reports the bundle under the 160 KB gzip budget; on a phone with the target language installed a four-year-old profile hears the first task spoken (a missing voice is silent, not an error). Status: bundle check automated; phone speech smoke **performed 2026-09-26** by the owner on a phone with a Russian voice — the first task was heard.
- Known limitation F-001: email is unverified and recovery is operator-assisted; the parent help text states it.
