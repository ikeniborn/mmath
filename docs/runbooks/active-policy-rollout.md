# Active policy rollout and rollback

Active mode lets the Framework System One proposal decide the next action instead of the rules, but only inside the legal action set the rules compute and only above a confidence threshold. This runbook is the checkpoint that gates activation and the drill that reverts it.

## What active mode can and cannot do

- The rules compute the allowed actions first (`repeat`, `hint`, `no_hint`, `switch` when other skills are enabled, `easier`/`harder` only in automatic mode within the band limits, `harder` only after five unhinted correct answers and never during an error streak). Fixed difficulty never offers a band change. The proposal is post-validated against this set even though the same set was sent as the question criteria.
- The proposal is applied only when its action is legal and its confidence is a number at or above `MMATH_ACTIVE_CONFIDENCE_THRESHOLD`. Otherwise the rule action applies and the audit row stores the reason: `illegal_action`, `confidence_low`, `confidence_missing`, or the transport failure (`busy`, `timeout`, `http_4xx`, `http_5xx`, `malformed`, `oversized`, `network`). A row with no reason means the proposal itself was applied.
- Issued problems are immutable: switching the mode never rewrites a task a child already sees, and the pending answer of an open session stays valid across a restart.
- The 350 ms total deadline, the single audit row per transition, the identity-free state and the token handling are the same as in shadow mode (`framework-integration.md`).

Coverage: `backend/tests/unit/test_confidence_gate.py`, `backend/tests/integration/test_active_policy.py` (fixed band, gate failures, error streak and band ceiling, immutability across mode changes, configuration refusal).

## Checkpoint before activation (human)

Activation is refused by configuration until all of the following are recorded on the task ledger as a decision:

1. Framework publishes the System One route and confirms the meaning of the returned probability; the shadow smoke ran with synthetic state.
2. The offline evaluation (`policy-evaluation.md`) over shadow evidence shows the calibration bins and the illegal-proposal rate; the threshold is chosen from that report. 0.8 is the proposed value from the design, not a measured one.
3. Latency from the same report: p50/p95/max over answered calls with the sample count, timeouts counted separately. Target: p95 under 500 ms on CPU, 100 ms desirable on GPU, and the deadline-fallback share acceptable to the operator.
4. The rollout decision names the threshold, the evidence export used and the person authorizing; its ledger event id goes into `MMATH_ACTIVE_ROLLOUT_AUTHORIZATION`.

Until then `MMATH_POLICY_MODE=active` fails at startup with the missing variable named; do not bypass it by inventing a value.

## Enabling active mode

```bash
# .env: MMATH_FRAMEWORK_URL, MMATH_FRAMEWORK_MODEL, MMATH_FRAMEWORK_TOKEN_PATH, MMATH_ACTIVE_CONFIDENCE_THRESHOLD, MMATH_ACTIVE_ROLLOUT_AUTHORIZATION
docker compose --env-file .env -f compose.yaml -f deploy/compose.public.yaml -f deploy/compose.active.yaml up -d --build --wait
docker compose --env-file .env -f compose.yaml -f deploy/compose.public.yaml logs api | grep 'policy runtime'
```

The `policy runtime` log line shows `policy_mode`, the threshold and the authorization reference; the token is never logged. `/internal/metrics` (reachable only inside the compose network, never through the edge) exposes `mmath_fallback_total` by reason and `mmath_policy_decision_latency_ms{mode="active"}` with its sample count; watch them for the first sessions.

## Rollback

Rollback is a configuration change and an API restart; the database, sessions and progress are untouched.

```bash
docker compose --env-file .env -f compose.yaml -f deploy/compose.public.yaml up -d --no-deps api
docker compose --env-file .env -f compose.yaml -f deploy/compose.public.yaml logs api | grep 'policy runtime'
```

Dropping the overlay returns `MMATH_POLICY_MODE` to `rules`; `--no-deps api` restarts only the API container, the web container and the external database keep serving. Verify with `/health/ready` and one played task; the open session continues from its issued problem. Record the rollback with its reason on the task ledger.
