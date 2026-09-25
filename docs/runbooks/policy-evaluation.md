# Learning evidence export and offline evaluation

Every committed policy decision is auditable and exportable as pseudonymous learning evidence. The export and the evaluation are operator-triggered, deterministic and repeatable over the same evidence; they never train a model, assign children to cohorts or contact Framework.

## What a record contains

One JSON line per decision with exactly six top-level keys, filtered through a recursive allowlist so no database or provider field outside the schema can appear:

- `state`: the aggregated, identity-free policy state at decision time (skill, band, mode, counts, streaks, mastery).
- `allowed_actions`, `decision` (proposed action, rule action, confidence when the provider supplied one, provider, sanitized failure code, fallback reason, latency), `applied_action`.
- `versions`: policy mode, model alias, rules version, mastery formula version.
- `outcome`: `prior_5` and `next_5` windows (count, accuracy, average valid response time) over accepted attempts of the same child and skill, `complete` (five subsequent attempts exist), `session_completed` (`true`/`false`, or `null` while the session is still active), `returned` (`true` when a later session exists, `false` only after the seven-day observation window, otherwise `null`).

Missing evidence stays `null` or `complete: false`; it is never converted into success or failure. Retries and replays add no records because outcomes derive from committed, deduplicated attempts.

## Export

Run on the API host (or anywhere with the DSN); the output path must be a new file.

```bash
cd backend
MMATH_DATABASE_URL=postgresql+psycopg://... uv run --project . python -m mental_math.policy.export --out /path/to/new/evidence-$(date +%Y%m%dT%H%M%SZ).jsonl
```

Add `--overwrite` only to replace a file deliberately. Store exports with the same care as backups; although pseudonymous, they describe children's learning.

## Offline evaluation

```bash
cd backend
uv run --project . python -m mental_math.policy.evaluation /path/to/evidence.jsonl
```

The JSON report contains: record, proposal and failure counts; agreement with rules; illegal proposal rate; fallback rate; latency p50/p95/max; calibration bins (agreement with the applied rule action per confidence bin, not a probability of learning benefit); the LLD candidate reward `0.40 × accuracy gain + 0.25 × speed gain + 0.20 × completion + 0.15 × retention` averaged over complete windows only, with the number of incomplete windows shown.

The report states explicitly: shadow outcomes follow the applied rule action, so nothing here establishes a causal benefit of the unchosen model action. Fine-tuning, Framework model residency and any A/B cohort experiment require separate authorization and a reviewed experiment decision.
