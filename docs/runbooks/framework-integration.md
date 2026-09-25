# Framework System One integration (policy modes)

mmath decides the next task with deterministic rules. The Framework GPU platform can additionally propose an action through Laya System One. Deployment policy modes: `rules` (default, no network call), `shadow` (the proposal is recorded, the rule action is applied), `active` (the gated proposal is applied; opt-in only through `active-policy-rollout.md`, which requires verified confidence semantics and an offline calibration checkpoint first).

## Contract in use

Source: framework wiki `runbook/laya-systemone-model-usage` and `specification/llm-runtime-manager` (2026-09-25).

- Route: `POST {MMATH_FRAMEWORK_URL}/v1/systemone` through Framework GPU Tools; discovery `GET /v1/systemone/models`. Never the Laya or Runtime Manager loopback ports.
- Authentication at the Internet edge: bearer `frameworkEdgeToken`, read from the file at `MMATH_FRAMEWORK_TOKEN_FILE` (mounted by the shadow overlay from `MMATH_FRAMEWORK_TOKEN_PATH`, a host file with mode `600`). Reviewed direct-LAN access may omit the token. The token never appears in logs, metrics, audit rows or repository files.
- Request: `{"model": alias, "state": {...}, "questions": {"next_action": {"type": "choice", "criteria": [allowed actions]}}}`. Aliases `laya-auto`, `laya-english`, `laya-multilingual`. The state is the aggregated, identity-free policy state (skill, band, mode, counts, streaks); no account, child or session identifiers.
- Response: `{"answers": {"next_action": <string or {"choice", "probabilities"}>}, "usage": {...}, "routing": {"model": alias}}`. A probability for the chosen action is stored as confidence when present; otherwise confidence is null. Confidence semantics are **not verified**; active mode therefore stays behind the rollout checkpoint in `active-policy-rollout.md`.
- Limits and failures: 2 MiB request/response, 50,000-character state, 64 questions. Concurrent inference answers `429 systemone_busy` (`Retry-After: 1`); mmath records `busy` and never retries or queues. 400/413/422 → `http_4xx`, 502/503/504 → `http_5xx`, unparsable or missing answer → `malformed`, body over the limit → `oversized`, connection problems → `network`, total deadline → `timeout`.

## Guarantees

- One total deadline of 350 ms wraps the whole call (pool, connect, read); HTTPX per-operation timeouts alone are not a total bound. On expiry the answer transaction continues with the rule action and `mmath_inference_deadline_total` increments.
- No failure mutates the allowed-action set or blocks a valid arithmetic answer; every transition writes exactly one audit row with policy state, allowed actions, policy mode, provider/model, proposal or sanitized failure, rule action, applied action, latency and fallback reason.
- Fixed difficulty never offers `harder`/`easier` on either path; unknown or illegal proposals are recorded and the rule action applies.
- Readiness ignores Framework availability; rules play continues when the model is unavailable.

## Current status

The Framework integration task reports **no production publication**: Runtime Manager and GPU Tools do not yet contain System One routes and Laya aliases are not publicly callable. Shadow mode is therefore verified only with the fake transport and HTTP mocks. A synthetic live smoke (state without child data) runs only after the framework owner records the publication and gives explicit authorization; record model/route provenance and status codes, never the bearer.

## Enabling shadow mode

```bash
# .env: MMATH_FRAMEWORK_URL, MMATH_FRAMEWORK_MODEL, MMATH_FRAMEWORK_TOKEN_PATH (host file, mode 600)
docker compose --env-file .env -f compose.yaml -f deploy/compose.public.yaml -f deploy/compose.shadow.yaml up -d --build --wait
```

Rollback: remove the shadow overlay and restart only the API; retained sessions and progress stay valid.
