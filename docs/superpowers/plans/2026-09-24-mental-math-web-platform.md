---
topic: mental-math-web-platform
review:
  plan_hash: 203196df748c1163
  last_run: 2026-09-24
  phases:
    structure: { status: passed }
    coverage: { status: passed }
    dependencies: { status: passed }
    verifiability: { status: passed }
    consistency: { status: passed }
  findings: []
chain:
  intent: docs/superpowers/intents/2026-09-24-mental-math-web-platform-intent.md
  spec: docs/superpowers/specs/2026-09-24-mental-math-web-platform-design.md
---
# Mental Math Web Platform Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking. Delegation still requires separate user authorization; default execution is parent-owned.

**Status:** approved

**Goal:** Deliver a child-friendly web arithmetic game with parent accounts, independent child progress, automatic/fixed difficulty, reliable resume, Docker deployment, connected mobile installation and guarded GPU Framework integration.

**Architecture:** React/TypeScript/Vite static frontend and a modular FastAPI API share an origin through Caddy. PostgreSQL owns accounts, learning sessions, attempts, mastery and policy evidence. GPU Framework is an external inference dependency; the base game remains usable without it.

**Tech Stack:** React, TypeScript, Vite, React Router, CSS Modules, Python/FastAPI/Pydantic/Uvicorn, SQLAlchemy/psycopg/Alembic, PostgreSQL 17, HTTPX, Argon2id, Caddy, Docker Compose, pytest, Vitest/Testing Library and Playwright.

**Spec:** [approved design](../specs/2026-09-24-mental-math-web-platform-design.md), body hash `c569f53d52d026cd`.

**Intent:** [approved intent](../intents/2026-09-24-mental-math-web-platform-intent.md), body hash `1e77a63f4c624d1c`.

## Global Constraints

- Retain React + TypeScript frontend, Python + FastAPI backend and PostgreSQL persistence. Application data and policy authority reside on the backend.
- Parent accounts use email/password; profiles and progress are separated by child and protected by account ownership.
- Support both automatic and fixed difficulty; automatic is the default. Fixed difficulty never bypasses allowed operations, numeric bounds or session limits.
- Use GPU Framework API for Laya with endpoint and credential supplied at deployment. Do not embed a Framework token in frontend code, generated assets, logs or repository files.
- Preserve deterministic mathematics, an independent Student Model, pre/post policy constraints, bounded action space, fallback, shadow evaluation and policy-decision history including state, model version, output, applied action and subsequent outcomes.
- Preserve the local/operator-controlled data boundary of ADR/HLD. Internet access to mmath does not authorize sending child information to third-party AI services.
- Docker deployment must distinguish public TLS access from optional LAN HTTP access. PWA installation and service-worker features require an appropriate secure origin.
- Do not implement offline gameplay, deferred client/server attempt synchronization, or Framework model lifecycle management in this scope.
- The current task delivers this plan, not its implementation. No application/runtime code is created until a separate execution authorization.
- Initial email is an unverified login identifier; password recovery is operator-assisted. Spec warning F-001 was accepted. Do not silently add SMTP, verification mail or self-service reset.
- Product text is Russian; code comments, repository documentation and wiki text are English. Child controls are at least 48 by 48 CSS pixels; layouts support 320 CSS-pixel width and 200% zoom.
- Use the approved task profile only as routing metadata. No automatic parent model/session switching, production deployment, Framework activation or credential discovery.
- Pin supported dependency patches and production image digests during Task 1. Preserve source documents and add only the documented supersession links.

## Delivery Order and Outcomes

| Task | Slice | Observable result | Depends on | Intent |
|---|---|---|---|---|
| T1 family access | S1a | Parent can sign in and maintain independent child profiles | None | O1, O5 |
| T2 first durable lesson | S1b | Child completes a basic lesson; accepted answers survive restart | T1 | O2, O4, O7 |
| T3 child navigation and resume | S2 | Child can use hints, leave and resume the exact saved phase | T2 | O2, O4 |
| T4 skill adaptation | S3 | Automatic default and fixed mode work across the baseline skill catalogue | T3 | O3, O7 |
| T5 public release operations | S4 | Operator has a verified TLS/LAN deployment and restore procedure | T4 | O1, O5 |
| T6 connected mobile installation | S7 | The same online game installs and launches on phones | T5 | O6 |
| T7 Framework shadow integration | S5 | Rules remain authoritative while real model proposals are recorded | T4; Framework checkpoint | O7 |
| T8 learning evidence | S8 | Operator can export pseudonymous outcomes and compare candidate policies offline | T7 | O7 |
| T9 guarded model adaptation | S6 | Evaluated model proposals influence eligible tasks with deterministic fallback | T8; calibration/rollout checkpoint | O3, O7 |

O8 is closed by this plan's task/interface/verification and coverage sections, not by inventing another runtime feature. T6 is independent of T7–T9. T8 precedes T9 so active-mode authorization can rely on evaluation evidence. T1–T4 are development/LAN increments; T5 is the first public release checkpoint. S1's fixed-band lesson is an intermediate increment; T4 establishes the final automatic-default behavior.

Do not open nine branches or task pages while planning. Keep this parent topic authoritative. During authorized execution, record each task's start, tests, review and outcome in the parent ledger. New independent topics require an explicit handoff and consistent artifact names.

## Repository Layout and Ownership

The current repository contains documentation only. Paths below are future implementation targets, not claims that files exist now.

| Paths | Responsibility | First owner task |
|---|---|---|
| backend/pyproject.toml, backend/uv.lock, backend/Dockerfile | Python dependencies and image | T1 |
| backend/mental_math/main.py, config.py, db.py | API composition, deployment config and per-request DB unit of work | T1 |
| backend/mental_math/accounts/{models,schemas,service,routes,security,cli}.py | Account/session/CSRF/parent confirmation and operator recovery | T1 |
| backend/mental_math/players/{models,schemas,service,routes}.py | Child ownership and profile settings | T1 |
| migrations/env.py, migrations/versions/0001_accounts.py | Initial database schema | T1 |
| backend/mental_math/game/{models,schemas,engine,generator,validator,routes}.py | Issued problems, sessions, attempts, atomic game flow | T2 |
| backend/mental_math/game/{constraints,hints,catalogue}.py | Eligible problems, deterministic hints and skill definitions | T3/T4 |
| backend/mental_math/student/{models,state,mastery,errors}.py | Independent skill aggregates and error classification | T2/T4 |
| backend/mental_math/policy/{types,fallback,service}.py | Policy contracts, modes and constrained rules | T2/T4 |
| backend/mental_math/policy/{framework,outcomes,export,evaluation}.py | Framework transport and later evaluation evidence | T7/T8 |
| frontend/package.json, package-lock.json, vite.config.ts, tsconfig.json, index.html | Frontend build | T1 |
| frontend/src/{main.tsx,app.tsx,api.ts,api-types.ts,styles.css} | Router, same-origin API, generated schema types and design tokens | T1 |
| frontend/src/features/{accounts,players,game,progress}/ | Screen components, CSS Modules and colocated component tests | T1–T4 |
| frontend/src/features/game/{sessionReducer.ts,pendingSubmission.ts} | Versioned snapshots and one in-flight retry record | T2/T3 |
| compose.yaml, compose.test.yaml, deploy/Dockerfile.web, deploy/Caddyfile | Development/LAN baseline and isolated test DB | T1 |
| deploy/{compose.public.yaml,compose.lan-http.yaml,Caddyfile.public,Caddyfile.lan-http} | Explicit release modes | T5 |
| frontend/public/{manifest.webmanifest,sw.js,offline.html,icons/} | Public PWA shell; no personal API cache | T6 |
| backend/tests/{conftest.py,contracts/,integration/,unit/}, frontend/e2e/ | Executable acceptance evidence | Each producing task |
| scripts/export_openapi.py, scripts/check_contract.py, docs/runbooks/ | Contract checks and deployment/recovery documentation | T1/T5 |

Each task owns its listed paths and only necessary edits to its consumed interfaces. Future workers are not alone in the codebase and must preserve other edits. Tests for concurrency use real PostgreSQL, never an in-memory substitute.

## Shared Interfaces and Test Harness

T1 creates a Python package rooted at `backend/mental_math`; pytest uses async tests and fixtures with one disposable PostgreSQL database per test worker. The test Compose project publishes only a loopback database endpoint and uses an isolated volume. Production volumes and credentials are never reused.

T1 fixtures, implemented in `backend/tests/conftest.py`, expose:

- `client`: HTTPX AsyncClient against the actual FastAPI ASGI app.
- `family`: a test helper with `parent_id`, `player_id`, authenticated cookie jar and current CSRF token. Its async `get(path)` and `post(path, json=...)` call real routes and attach CSRF; `post` does not hide HTTP failures.
- `other_family`: a separately registered account with independent cookie jar.
- `db`: an SQLAlchemy test-session factory; concurrent operations obtain separate sessions.
- `policy_fake`: injected test transport, configured through dependency overrides only; no test-only production endpoints.

T2 extends fixtures with `lesson`, holding a real issued session/problem and version, and `counts(player_id)` querying counts from the database. Browser fixtures create accounts through routes and seed controlled exercise sequences through test database helpers; correct answers never become a public API field.

Shared backend contracts are explicit dataclasses/Pydantic models in the named module:

```python
# accounts/service.py
async def require_account(request: Request, db: AsyncSession) -> Account: ...
# players/service.py
async def owned_player(db: AsyncSession, account_id: UUID, player_id: UUID, *, lock: bool) -> Player: ...
# game/engine.py
async def start_session(db: AsyncSession, account_id: UUID, player_id: UUID) -> SessionSnapshot: ...
async def submit_attempt(db: AsyncSession, account_id: UUID, session_id: UUID, command: SubmitAttempt) -> AttemptResult: ...
async def advance_session(db: AsyncSession, account_id: UUID, session_id: UUID, attempt_id: UUID, expected_version: int) -> SessionSnapshot: ...
# policy/types.py
class PolicyTransport(Protocol):
    async def predict(self, state: PolicyState, allowed_actions: tuple[str, ...]) -> PolicyProposal: ...
```

These are signatures, not implementation placeholders. `SubmitAttempt` contains submission_id, problem_id, answer, response_ms (nullable) and expected_version. `SessionSnapshot` contains id, player_id, version, state, phase, public current problem or null, saved feedback or null and effective profile settings. `AttemptResult` contains attempt_id, correct, feedback, public pending next problem or null and the current SessionSnapshot. PolicyState contains aggregated skill/session/error/timing data only; PolicyProposal contains action, confidence or null, model/version and sanitized failure code or null. `PolicyDecision` adds allowed actions, mode, proposed/applied actions, latency and fallback reason.

The unit of work owns commit/rollback; helper methods do not commit independently. Game mutations acquire child then session locks in that order. The test suite asserts atomicity around the actual commit boundary.

All shell checks below run from the repository root unless a subshell explicitly changes directory. T1 creates the referenced package scripts: frontend `typecheck`, `test`, `build`, `test:e2e`; Python execution uses the backend project. No command is represented as having passed before execution.

## Task 1: Family Access and Child Profiles

**Closure:** S1a, O1/O5; spec sections 3, 5, 7 and AUTH-01/02/04.

**Files:** Create the T1 paths in the ownership table; create `backend/tests/integration/test_accounts.py`, `test_player_ownership.py`, `test_parent_settings.py`, `frontend/src/features/accounts/AccountPage.tsx`, `frontend/src/features/players/PlayerPicker.tsx`, `PlayerSettings.tsx` and `frontend/e2e/family-access.spec.ts`. Create `docs/runbooks/account-recovery.md` and a deployment example containing only dummy values.

**Produces:** authenticated parent sessions, scoped profiles, CSRF handling, dependency locks, migration harness, API contract generation, browser shell and test fixtures. Profile schema already includes automatic/fixed mode even though actual adaptation arrives in T4.

- [ ] Build the minimal package/test harness and isolated PostgreSQL fixture. Pin dependencies/images and install the declared test tools. Ensure missing configuration fails explicitly; no real secret defaults.
- [ ] Add route-level account isolation, CSRF, parent confirmation, expiry, login throttling and recovery tests. Example red acceptance:

```python
@pytest.mark.asyncio
async def test_other_parent_cannot_read_child(family, other_family):
    response = await other_family.get(f"/api/v1/players/{family.player_id}")
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_profile_defaults_to_automatic(family):
    response = await family.get(f"/api/v1/players/{family.player_id}")
    assert response.status_code == 200
    assert response.json()["mode"] == "automatic"
```

- [ ] Run the tests and record a failing behavioral assertion once routes are callable. Implement account/profile tables, constraints and ownership predicates. Store hashes of random session identifiers, never plaintext passwords/session tokens.

```python
statement = select(Player).where(Player.id == player_id, Player.account_id == account_id)
if lock:
    statement = statement.with_for_update()
player = await db.scalar(statement)
if player is None:
    raise HTTPException(status_code=404, detail={"code": "not_found"})
```

- [ ] Implement Argon2id password verification, session rotation/revocation, 30-day absolute expiry, pre-auth/authenticated CSRF and 10-minute parent-confirmation window. Bound password input at 128 characters with minimum 12; normalize email casing consistently and enforce uniqueness. Use generic failed-login responses. Initial throttle: five failed attempts per account/IP pair per 15 minutes, then temporary rejection; test expiry and avoid indefinite account locks. These values operationalize the approved bounded validation/throttling requirement, not new user features.
- [ ] Implement the operator recovery entry point using an interactive password prompt, explicit account confirmation and transactional revocation of existing sessions. Never accept a password command-line argument or log its value. No HTTP recovery route or outgoing email is added.
- [ ] Build register/login, child selection and settings screens. Validate at least one enabled topic and age 5–10; settings mutations require parent confirmation. Show the unverified-email/recovery limitation in the parent account help. Export OpenAPI and generate frontend types with a pinned generator; the schema/type comparison script exits nonzero on drift.
- [ ] Verify focused checks, inspect the exact diff and commit the task only after they pass.

```bash
docker compose -f compose.test.yaml up -d --wait postgres-test
uv run --project backend pytest backend/tests/integration/test_accounts.py backend/tests/integration/test_player_ownership.py backend/tests/integration/test_parent_settings.py -q
(cd frontend && npm run typecheck && npm run test -- --run && npm run build)
uv run --project backend python scripts/check_contract.py
(cd frontend && npm run test:e2e -- family-access.spec.ts)
git diff --check
```

**Expected:** own profiles work, cross-family requests do not; invalid CSRF and unconfirmed settings writes fail; synthetic recovery revokes old sessions; migrations work on empty test DB. Commit: `feat(accounts): add parent access and child profiles`.

## Task 2: First Durable Lesson

**Closure:** S1b, O2/O4/O7; spec sections 6, 8–9 and RESUME-02/03/05.

**Files:** Create T2 game/student/policy paths, `migrations/versions/0002_game_state.py`, `backend/tests/integration/test_attempt_atomicity.py`, `test_attempt_idempotency.py`, `test_session_restart.py`, `backend/tests/unit/test_addition.py`, `frontend/src/features/game/GamePage.tsx`, `sessionReducer.ts`, `pendingSubmission.ts` and `frontend/e2e/first-lesson.spec.ts`.

**Consumes:** T1 ownership/session/DB interfaces. **Produces:** start/read/submit/advance/finish endpoints, immutable problems, transactionally persisted attempts and feedback, one active session per child, a basic addition exercise and summary. Initial state aggregates count attempts/correctness; T4 completes the full mastery model.

- [ ] Add property tests for addition band 0 and real-database retry/rollback tests. The fixture's command holds a constant submission id/body across retries:

```python
@pytest.mark.asyncio
async def test_retry_does_not_duplicate(family, lesson, counts):
    path = f"/api/v1/sessions/{lesson.session_id}/attempts"
    first = await family.post(path, json=lesson.command)
    second = await family.post(path, json=lesson.command)
    assert first.status_code == second.status_code == 200
    assert first.json()["attempt_id"] == second.json()["attempt_id"]
    assert (await counts(family.player_id))["attempts"] == 1
```

- [ ] Implement schema uniqueness for one unfinished session per child and one attempt per session/problem. Persist the deduplication fingerprint and immutable result. Ensure replay authorization precedes lookup. Different payload reuse or a second id for an answered problem returns 409.
- [ ] Implement the transaction in `engine.py`: child lock, version validation, deterministic grade, attempt, statistics, rules decision, pending problem/feedback, version increment, commit. Fault-injection tests raise before commit and drop the HTTP response after commit; production code has no public injection switches.

```python
async with db.begin():
    player = await owned_player(db, account_id, player_id, lock=True)
    # Resolve session/problem, reject stale input, then write all state together.
    # No repository method performs its own commit.
```

- [ ] Add all state-transition endpoints now, including idempotent advance and finish. Set timing origin when the next problem becomes active, not when generated. Save the session's profile snapshot; changing profile settings cannot rewrite it. Return committed server snapshots; never return the server-only correct answer for an unanswered task.
- [ ] Add the browser reducer that ignores older snapshots and stores exactly one pending retry record in sessionStorage. Clear it on confirmed result, logout and profile switch. Keep answer/feedback states explicit; never optimistically update score.

```typescript
function acceptSnapshot(current: SessionSnapshot, incoming: SessionSnapshot): SessionSnapshot {
  return incoming.version >= current.version ? incoming : current;
}
```

- [ ] Verify start, answer, feedback, continue, finish and restart using real persistence. Commit only this completed increment.

```bash
uv run --project backend pytest backend/tests/unit/test_addition.py backend/tests/integration/test_attempt_atomicity.py backend/tests/integration/test_attempt_idempotency.py backend/tests/integration/test_session_restart.py -q
(cd frontend && npm run test -- --run src/features/game && npm run typecheck)
(cd frontend && npm run test:e2e -- first-lesson.spec.ts)
git diff --check
```

**Expected:** one accepted answer creates one attempt and one applied decision; rollback creates none; response-loss retry and database-preserving restart retain position. Commit: `feat(game): persist the first lesson atomically`.

## Task 3: Child Navigation, Hints and Resume

**Closure:** S2, O2/O4; UX-01/02, RESUME-01/04/06 and MODE-04.

**Files:** Modify `game/engine.py`, `game/routes.py`, `game/schemas.py`, `GamePage.tsx`, `sessionReducer.ts`, `pendingSubmission.ts`; create `game/hints.py`, `frontend/src/features/game/{NumberPad,Feedback,ChildHome,SessionSummary}.tsx`, associated CSS Modules, `backend/tests/integration/{test_resume_phases,test_concurrent_answers,test_hints,test_profile_snapshots}.py`, `frontend/e2e/{resume,child-navigation}.spec.ts`.

**Consumes:** T2 durable snapshot/advance/finish. **Produces:** complete child journey, saved hint state, reliable multi-browser reconciliation and accessible controls.

- [ ] Write answer-phase/feedback-phase reload tests and simultaneous requests using separate database sessions. Verify the losing browser receives a version conflict/current snapshot, not a second grade. Add cross-child concurrency test showing independent progress.
- [ ] Add idempotent hint storage under the same child lock. Render counters/ten-frames/number line from deterministic operands; record hint exposure once before returning content. Include retry after a dropped hint response.

```python
@pytest.mark.asyncio
async def test_hint_is_recorded_once(family, lesson, counts):
    path = f"/api/v1/sessions/{lesson.session_id}/hint"
    command = {"problem_id": str(lesson.problem_id), "expected_version": lesson.version}
    first = await family.post(path, json=command)
    second = await family.post(path, json=command)
    assert first.status_code == second.status_code == 200
    assert (await counts(family.player_id))["hinted_problems"] == 1
```

- [ ] Reconcile stale hint versions only when the same already-exposed hint is being replayed; another answered/current problem never receives hint mutations. Keep the same expected-version discipline for other game mutations.
- [ ] Build large touch targets, keyboard entry, visible focus, live feedback announcement, reduced-motion styles and the persistent Resume action. Keep the next problem hidden until advance. Preserve draft digits only while the current task is visible/pending; refresh may discard an unsubmitted draft.
- [ ] Measure foreground time with pause/visibility listeners; validate timing samples server-side and exclude invalid samples from speed scoring. Enforce 5/10/15-minute configured limits at transitions; an explicit Finish never drops accepted attempts.
- [ ] Run race, navigation and accessibility checks; review widths/zoom manually. Update screenshots only when intentional; no snapshot-only acceptance.

```bash
uv run --project backend pytest backend/tests/integration/test_resume_phases.py backend/tests/integration/test_concurrent_answers.py backend/tests/integration/test_hints.py backend/tests/integration/test_profile_snapshots.py -q
(cd frontend && npm run test:e2e -- resume.spec.ts child-navigation.spec.ts)
(cd frontend && npm run typecheck && npm run test -- --run src/features/game)
git diff --check
```

**Expected:** hint replay is safe, stale answers cannot overwrite current state, 320/768/1280 layouts and 200% zoom remain usable, keyboard and touch complete the same journey. Commit: `feat(ui): add accessible practice and exact resume`.

## Task 4: Automatic and Fixed Skill Practice

**Closure:** S3, O3/O7; MODE-01–04, MATH-01, STUDENT-01/02; all baseline arithmetic and student capabilities.

**Files:** Create `game/catalogue.py`, `game/constraints.py`, `student/mastery.py`, `student/errors.py`, `frontend/src/features/progress/ProgressPage.tsx`, `backend/tests/unit/{test_catalogue,test_mastery,test_error_classifier,test_rule_policy}.py`, `backend/tests/integration/test_difficulty_modes.py`; modify generator/student/policy services, player validation, progress routes and game views; add `migrations/versions/0003_skill_state.py`.

**Consumes:** durable attempts, timing/hint flags and profile snapshots. **Produces:** skill catalogue, full mastery aggregates, automatic default/fixed invariance and progress history.

- [ ] Implement an explicit catalogue table mapping code, operation, supported band, operand/result predicates and hint renderer. Cover addition/subtraction within 10/20/50, doubles, near-doubles, make-ten and multiplication by 2/3. Additional tables 4–10 are not necessary to close the baseline and are not silently added. Invalid fixed-mode topic/band combinations show supported alternatives.
- [ ] Before each generator implementation, add bound/answer property tests over its eligible pairs. Preserve nonnegative subtraction, bridge-ten distinctions and deterministic grading. Classifier precedence is correctness, off-by-one, concatenation, subtraction-confusion, other.
- [ ] Test exact aggregation and the approved formula against independent worked examples. Persist formula version and per-skill automatic band. Unknown mastery stays unknown before the first attempt; invalid timing cannot increase speed score.

```python
def test_mastery_known_window():
    from mental_math.student.mastery import calculate_mastery
    value = calculate_mastery(recent_accuracy=0.5, speed_score=1.0, consistency=0.25)
    assert value == pytest.approx(0.60)
```

- [ ] Implement pure mastery calculation and rule policy, then integrate them within T2's transaction. Policy restrictions apply before and after selection. Fixed mode cannot offer or apply harder/easier; automatic promotion requires five correct unhinted answers, one band maximum, and never follows three errors.

```python
def calculate_mastery(*, recent_accuracy: float, speed_score: float, consistency: float) -> float:
    return min(1.0, max(0.0, 0.50 * recent_accuracy + 0.30 * speed_score + 0.20 * consistency))
```

- [ ] Make automatic the functional default. Add progress/skill history and settings indicators. Profile updates affect new sessions only; fixed mode still updates mastery. Add rules-only decision audit rows with state/action/outcome links.
- [ ] Verify focused domain and route sequences, schema contracts and the full browser journey with automatic and fixed profiles.

```bash
uv run --project backend pytest backend/tests/unit/test_catalogue.py backend/tests/unit/test_mastery.py backend/tests/unit/test_error_classifier.py backend/tests/unit/test_rule_policy.py backend/tests/integration/test_difficulty_modes.py -q
uv run --project backend python scripts/check_contract.py
(cd frontend && npm run test:e2e -- difficulty-modes.spec.ts)
git diff --check
```

Create `frontend/e2e/difficulty-modes.spec.ts` as part of this task. **Expected:** all baseline skills have verified bounds; fixed difficulty never moves; automatic thresholds and per-child/per-skill isolation hold. Commit: `feat(practice): add constrained adaptive skill progression`.

## Task 5: Public Docker Release and Recovery

**Closure:** S4, O1/O5; AUTH-03/04, OPS-01/02 and UX-03.

**Files:** Create T5 deployment overlays and Caddyfiles, `deploy/test.public.env`, `deploy/test.lan.env` (synthetic configuration only), `docs/runbooks/{deployment,backup-restore,release-checklist}.md`, `backend/tests/integration/{test_deployment_security,test_readiness}.py`, `scripts/check_deployment.py`; modify `config.py`, `main.py`, compose health/migration settings and the T1 recovery runbook.

**Consumes:** complete T4 game and account state. **Produces:** verified public/LAN configurations, health contracts and restore evidence. Public exposure itself is not automatic.

- [ ] Add startup/config tests proving public mode rejects an HTTP origin and that LAN HTTP requires explicit selection. Validate trusted proxy/Host settings. Test Secure/SameSite/HttpOnly flags and CSRF using the production configuration logic, not handcrafted responses.
- [ ] Package frontend build into Caddy image. Route API paths before SPA fallback and publish no database/API port. Add one-shot migrations; readiness checks DB/schema, not Framework. Add volume-preserving restart acceptance.
- [ ] Document a separate restore database/project and run a synthetic backup/restore drill. Compare account, attempt counts and resumed problem id, not just archive size. Never run volume-deletion commands against a user's deployment.

```python
def assert_restored_state(before, after):
    assert after["account_ids"] == before["account_ids"]
    assert after["attempt_count"] == before["attempt_count"]
    assert after["current_problem_id"] == before["current_problem_id"]
```

- [ ] Implement aggregate metrics and safe structured logging as specified; redact secret fields at the logging boundary and test with synthetic marker values. Include inference deadlines and fallback counts without high-cardinality labels. Validate that bundled assets contain no secret markers.
- [ ] Run configuration/security checks and a local isolated deployment. Complete supervised usability review for younger/older users with explicit human participation; record actionable findings without collecting identifying child data.

```bash
docker compose --env-file deploy/test.public.env -f compose.yaml -f deploy/compose.public.yaml config --quiet
docker compose --env-file deploy/test.lan.env -f compose.yaml -f deploy/compose.lan-http.yaml config --quiet
uv run --project backend pytest backend/tests/integration/test_deployment_security.py backend/tests/integration/test_readiness.py -q
uv run --project backend python scripts/check_deployment.py --isolated
git diff --check
```

The configuration commands use committed dummy test settings, never production secrets: `DEPLOYMENT_MODE=public` with `APP_ORIGIN=https://mmath.test`, or `DEPLOYMENT_MODE=lan-http` with a loopback HTTP test origin. Supply other required values as synthetic fixtures, and disable real certificate acquisition in the isolated harness. Do not print rendered secret configuration. `check_deployment.py --isolated` creates only uniquely named test resources and must fail rather than attach to existing non-test volumes.

**HUMAN CHECKPOINT:** obtain domain/DNS/TLS prerequisites and explicit authorization before public exposure; do not open firewall ports or install certificates on a live host during repository verification. **Expected:** clean deployment and restore checks, reviewed child usability findings, documented F-001 recovery limitation. Commit: `feat(deploy): add verified public and local deployment modes`.

## Task 6: Connected Mobile PWA

**Closure:** S7, O6; PWA-01. This can ship before Framework integration.

**Files:** Create the T6 public files, `frontend/src/features/accounts/ConnectionRequired.tsx`, `frontend/src/pwa.ts`, `frontend/e2e/pwa.spec.ts` and `docs/runbooks/mobile-installation.md`; modify app startup and edge cache headers.

**Consumes:** T5 secure same-origin deployment. **Produces:** standalone installation and connection-required behavior, without offline arithmetic or personal caches.

- [ ] Write browser tests proving install metadata is present and cache storage contains only allowlisted public shell assets. Test logout/profile switching before offline launch so another child's state cannot reappear from a cache.
- [ ] Implement a versioned precache of public assets and an offline shell. The worker must leave API traffic to the network and must not store API responses or queue mutation requests.

```javascript
self.addEventListener("fetch", (event) => {
  const url = new URL(event.request.url);
  if (event.request.method !== "GET" || url.pathname.startsWith("/api/")) return;
  // Only the explicit public-asset allowlist or navigation offline shell is cacheable.
});
```

- [ ] Add manifest/icons/standalone display and platform-appropriate installation help. Keep an existing pending submission intact on transient disconnect. A waiting worker updates only at a safe screen after user acceptance; it must not reload mid-answer.
- [ ] Verify Chromium service-worker/cache behavior and actual Android/iOS installation manually; desktop WebKit emulation is not evidence of iOS installation. Record device/browser versions in the release checklist.

```bash
(cd frontend && npm run build && npm run test:e2e -- pwa.spec.ts)
(cd frontend && npm run typecheck)
git diff --check
```

**Expected:** online installed journeys match web journeys; offline launch gives a connection message without prior child data; LAN HTTP remains ordinary web mode. Commit: `feat(pwa): add connected mobile installation`.

## Task 7: GPU Framework Shadow Policy

**Closure:** S5, O7; POLICY-01/02/04/05.

**Files:** Create `policy/framework.py`, `backend/tests/unit/test_framework_transport.py`, `backend/tests/integration/{test_shadow_policy,test_policy_deadline}.py`, `docs/runbooks/framework-integration.md`; modify `policy/types.py`, `policy/service.py`, config and dependency injection; add `migrations/versions/0004_policy_audit.py` if fields were not already created by T4.

**Consumes:** T4 policy state/actions/audit contract and per-child transaction. **Produces:** bounded injectable Framework transport, shadow mode and failure evidence.

**HUMAN CHECKPOINT:** before coding a real wire adapter, read the current Framework task/contract and obtain published route, authentication mode, aliases, request/response schema, model version/confidence semantics and operator privacy boundary. Do not invent `/v1/systemone` as a Framework route. Fake-transport tests can proceed independently; real-route completion and live smoke remain blocked until the contract exists. No runtime activation or model download belongs to this task.

- [ ] Add behavior tests for success, immediate 429, timeout, cancellation, HTTP error, oversized/malformed response and illegal actions. No failure may mutate the constraint set or stop a valid arithmetic transaction.

```python
@pytest.mark.asyncio
async def test_shadow_cannot_override_rules(family, lesson, policy_fake):
    policy_fake.action = "harder"
    policy_fake.mode = "shadow"
    result = await family.post(f"/api/v1/sessions/{lesson.session_id}/attempts", json=lesson.command)
    assert result.status_code == 200
    decision = await policy_fake.persisted_decision()
    assert decision.applied_action == decision.rule_action
```

Extend the fixture with `persisted_decision()` as a database query, not a mirror of the fake's response. The fake controls only transport input/output and mode configuration.

- [ ] Implement the reviewed contract using server-only configuration and a secret file where required. Strip user identity/credentials from state. Bound total pool/connect/read/cancellation time to 350 ms with an outer timeout; HTTPX's per-operation timeouts alone are not a total deadline. No retry or queue on 429.

```python
try:
    async with asyncio.timeout(0.350):
        proposal = await transport.predict(state, allowed_actions)
except TimeoutError:
    proposal = PolicyProposal.failure("timeout")
```

Implement `PolicyProposal.failure(code)` in `policy/types.py` to return a typed failure with null model/confidence/action and sanitized code. Catch only the reviewed transport/error taxonomy; do not swallow programming exceptions as normal model failures.

- [ ] Keep default mode rules. Shadow persists proposals and applies rule action; verify fixed mode and parameter bounds on both paths. Confirm aggregate state and safe provenance with the actual Framework contract, rather than accepting arbitrary provider JSON.
- [ ] Run fake-transport/deadline regressions and, only when authorized, a synthetic live contract smoke without child data. Record model/route provenance and response semantics, never the bearer.

```bash
uv run --project backend pytest backend/tests/unit/test_framework_transport.py backend/tests/integration/test_shadow_policy.py backend/tests/integration/test_policy_deadline.py -q
git diff --check
```

**Expected:** rules never change in shadow; busy/failed inference yields legal fallback, finite transaction duration and one applied audit row. Live readiness is reported separately from test completion. Commit: `feat(policy): integrate Framework shadow inference`.

## Task 8: Learning Evidence and Offline Evaluation

**Closure:** S8, O7; ADR-004/008, LLD outcome/reward data.

**Files:** Create `policy/outcomes.py`, `policy/export.py`, `policy/evaluation.py`, `backend/tests/unit/test_policy_evaluation.py`, `backend/tests/integration/test_policy_export.py` and `docs/runbooks/policy-evaluation.md`; extend audit outcome columns by `migrations/versions/0005_policy_outcomes.py`.

**Consumes:** committed T7 policy decisions and later attempts/session outcomes. **Produces:** pseudonymous export and reproducible offline comparison, not training or child cohort assignment.

- [ ] Define export records containing state, allowed actions, proposal/applied decision, policy/model versions, next-five correctness/active-time, completion and return signals. Mark incomplete windows explicitly. Count only subsequent accepted attempts of the same child/skill for accuracy/time; calculate retention from a later session, not a fabricated zero for an observation window still open.
- [ ] Add tests showing retries do not duplicate outcome entries and field allowlists exclude account email/name/password/token/cookie/headers. Use synthetic secret markers and check the serialized export, not just column names.

```python
def test_export_uses_allowlist(export_row):
    record = export_row.to_public_record()
    assert set(record) == {"state", "allowed_actions", "decision", "applied_action", "versions", "outcome"}
    assert "email" not in record["state"]
    assert "token" not in record["state"]
```

Define `PolicyExportRow` and its `to_public_record()` method in `policy/export.py`; create the `export_row` fixture from real persisted synthetic evidence. Nesting is recursively checked against the schema so malicious provider fields cannot bypass the top-level allowlist.

- [ ] Implement outcome assembly and deterministic metrics: agreement with rules, illegal proposal rate, fallback rate, latency, calibration where confidence is supported and the LLD candidate reward. Missing evidence is excluded or labeled incomplete, never converted into success. The report explicitly states that shadow outcomes follow the applied rule action and cannot establish causal benefit of the unchosen model action.
- [ ] Document operator-triggered export to an explicitly selected new file and synthetic evaluation commands. Do not overwrite an existing file by default. Fine-tuning, Framework residency and A/B cohort experiments require separate authorization.

```bash
uv run --project backend pytest backend/tests/unit/test_policy_evaluation.py backend/tests/integration/test_policy_export.py -q
git diff --check
```

**Expected:** repeatable reports over the same evidence, zero sensitive fields, incomplete outcomes visible, no unsupported superiority claim. Commit: `feat(policy): add learning evidence and offline evaluation`.

## Task 9: Guarded Active Policy

**Closure:** S6, O3/O7; POLICY-01/03 and HLD performance/reliability.

**Files:** Modify `policy/service.py`, `policy/types.py`, `game/constraints.py`, config and metrics; create `backend/tests/integration/test_active_policy.py`, `backend/tests/unit/test_confidence_gate.py` and `docs/runbooks/active-policy-rollout.md`.

**Consumes:** T7 verified transport and T8 evaluation evidence. **Produces:** opt-in active mode with documented rollback to rules.

**HUMAN CHECKPOINT:** verified confidence semantics and calibration evidence, accepted threshold and explicit rollout authorization. The spec's 0.8 is an initial proposal; do not silently activate it. Without usable confidence, remain in rules/shadow and report active rollout pending. Do not trigger model training or switch Framework deployments.

- [ ] Add adversarial tests covering fixed mode, error streaks, band limits, low/missing confidence, invalid action and saturated single-flight service. All failures must apply the same legal fallback contract.

```python
@pytest.mark.asyncio
async def test_active_cannot_raise_fixed_band(family, fixed_lesson, policy_fake):
    policy_fake.mode = "active"
    policy_fake.action = "harder"
    policy_fake.confidence = 1.0
    response = await family.post(f"/api/v1/sessions/{fixed_lesson.session_id}/attempts", json=fixed_lesson.command)
    assert response.status_code == 200
    assert response.json()["session"]["settings"]["difficulty_band"] == fixed_lesson.band
    assert response.json()["next_problem"]["difficulty_band"] == fixed_lesson.band
```

T9 adds `fixed_lesson` as a nonterminal real session fixture. Assert both snapshot and generated task band so a display-only invariant cannot hide an illegal task.

- [ ] Implement confidence and legal-action gates; preserve post-validation even when prefiltered actions were supplied. Store the reason whenever proposal and applied action differ. Already-issued problems are immutable across mode/config changes.
- [ ] Measure rule/shadow/active decision latency on the intended deployment with synthetic requests. Record p50/p95/max and sample count; retain the 500 ms CPU policy target and desirable 100 ms GPU target. Distinguish policy time from browser round-trip and timeout fallback counts. A missed target requires diagnosis or remaining in rules; it is not waived by tests.
- [ ] Verify rollback by switching app policy configuration to rules and restarting only the API as documented; retained sessions/progress remain valid. Run the relevant final suite once for the stable implementation fingerprint.

```bash
uv run --project backend pytest backend/tests/unit/test_confidence_gate.py backend/tests/integration/test_active_policy.py -q
uv run --project backend pytest backend/tests -q
(cd frontend && npm run typecheck && npm run test -- --run && npm run build && npm run test:e2e)
uv run --project backend python scripts/check_contract.py
git diff --check
```

**Expected:** model can influence legal automatic-mode transitions only; no model fault stops play or corrupts state; rollout evidence and rollback are reviewable. Commit: `feat(policy): enable evaluated constrained adaptation`.

## Verification, Documentation and Task Closure

Each task starts with a failing behavioral test, implements the smallest passing change, runs focused checks and records command, scope, exit status and code-state fingerprint. Record commit id plus uncommitted diff hash when relevant. For documentation/manual/device checks, record actual observations and environment; do not manufacture process exit codes.

Shared runtime/security/contract changes require related regression checks and a full relevant suite once on the final stable fingerprint. T5 and T6 releases must run that final suite even if T7–T9 are not ready; do not postpone their verification until optional integration. If T9 later changes the fingerprint, its final suite is new required evidence. Reuse unchanged passing evidence for review/branch finishing; do not repeat broad failures without a new hypothesis.

Every task updates relevant runbooks, source references and the parent iwiki ledger, then lints the touched pages. At implementation time, search/context existing GWT scenarios before changes; author explicit new specification scenarios alongside executable tests with real implements/verifies selectors. Do not invent selectors now, when implementation symbols do not exist. Missing code graph is recorded as graph_unavailable; tests/repository search remain required.

| Source requirement | Task evidence |
|---|---|
| O1 accounts and isolation | T1 auth/profile/recovery, T5 deployment security |
| O2 child navigation | T2 first lesson, T3 complete UI, T5 supervised review |
| O3 automatic/fixed | T4 modes/mastery, T9 active restrictions |
| O4 resume/integrity | T2 commit/retry, T3 phase/race, T5 backup/restore |
| O5 Docker/TLS/LAN | T1 skeleton, T5 release |
| O6 connected PWA | T6 installation/cache tests |
| O7 domain/policy preservation | T2 arithmetic, T4 catalogue/model, T7–T9 policy/evidence |
| O8 reviewable slices | This plan's task graph, exact ownership, interfaces and verification |
| ADR-001 / ADR-005 / ADR-007 | T1–T4 separate responsibilities with deterministic math/model |
| ADR-002 / ADR-003 / ADR-006 | T4/T7/T9 local Framework, small action space, constraints/fallback |
| ADR-004 / ADR-008 | T7 shadow, T8 evidence, T9 evaluated activation; training remains separate |
| HLD observability/performance | T5 metrics/logs, T7 deadlines, T9 measured targets |
| LLD catalogue/error/mastery | T4 property/sequence tests |
| LLD tables/API/Compose | T1–T5 migrations/contract/deployment checks |
| LLD training/reward/outcome | T8 incomplete-aware export and evaluation |

Expected results are the table above. Actual implementation evidence is absent at plan-authoring time. This document cannot close the application as delivered. The planning task can conclude only after plan review/approval and reconciliation of its documentation deliverables; a later execution task must reference this exact approved plan and its deferred human checkpoints.

## Human Checkpoints and Handoff

1. Approve this checked plan before any implementation. The existing instruction authorizes design/planning only.
2. Authorize application execution separately; default to parent-owned execution unless delegation is explicitly requested. Classify each task from its current security/integrity evidence, not task size.
3. Before T5 public exposure, authorize the actual target deployment and prerequisites. Before completion of UX-03 and T6 installation checks, arrange the required human/device participation.
4. Before T7 real transport completion, confirm the published Framework contract; before T9 active rollout, approve verified confidence/calibration and deployment changes.
5. Keep training and A/B experiments outside this plan's execution authority. Preserve their documented future capability without presenting them as shipped.

After plan approval, commit the approved plan before execution handoff. No execution option is activated by the act of approving the planning artifact alone.
