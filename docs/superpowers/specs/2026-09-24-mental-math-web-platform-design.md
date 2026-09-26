---
topic: mental-math-web-platform
review:
  spec_hash: c569f53d52d026cd
  last_run: 2026-09-24
  phases:
    structure: { status: passed }
    coverage: { status: passed }
    clarity: { status: passed }
    consistency: { status: passed }
  findings:
    - id: F-001
      phase: clarity
      severity: WARNING
      section: "7. Accounts and Security Boundary"
      section_hash: 3ec5ad9844815bf6
      fragment: "Public email is a login identifier in the initial design, not a verified claim of mailbox ownership."
      text: "Operator-assisted recovery and unverified email identity are explicit release limitations requiring user review."
      fix: "Approve this initial boundary or request an email verification/reset delivery slice before public release."
      verdict: accepted
      verdict_at: 2026-09-24
chain:
  intent: docs/superpowers/intents/2026-09-24-mental-math-web-platform-intent.md
---
# Mental Math Web Platform Design

**Date:** 2026-09-24
**Status:** approved
**Scope:** product architecture and vertical implementation slices; no application implementation or production deployment is authorized by this document.

## 1. Decision and Alternatives

Use a modular FastAPI application, PostgreSQL and a React + TypeScript SPA built with Vite. A Caddy container serves the static frontend and proxies same-origin API requests. GPU Framework remains an external deployment dependency owned by the operator.

| Approach | Benefit | Cost | Decision |
|---|---|---|---|
| React SPA + modular FastAPI | Independent visual components; one authoritative game model; small deployment | Browser routing and explicit request states | Selected; matches approved frontend direction |
| React SSR framework + FastAPI | Server-rendered public pages | Additional runtime and duplicated server boundaries; no current SEO requirement | Rejected for this scope |
| Separate account/game/policy services | Independent deployments | Distributed progress transactions and more operational components | Rejected; retain module boundaries within one backend |

HTMX was considered before intent approval. React + TypeScript is now a fixed input, not a decision reopened by this design.

## 2. Acceptance (from intent)

The following Desired Outcomes and Done-when criteria are copied verbatim from the approved intent. They describe future implementation acceptance; this design does not claim runtime success.

- O1 — A parent can register and sign in using email and password, select a child profile and access only their family's progress. Each child has independent settings, skills and history.
- O2 — A child aged 5–10 can identify how to start or resume a session, understand the current exercise, enter an answer and understand feedback. The design names these screens, primary actions and age-appropriate visual aids.
- O3 — Automatic difficulty is the default profile mode. Difficulty responds to the child's performance within profile settings and domain constraints. The parent can instead select fixed mode with a chosen difficulty; results continue to update history and the Student Model without automatic difficulty changes.
- O4 — Returning after closing the browser or restarting the application service preserves committed progress and offers continuation from the saved session position. The design specifies the authoritative saved state and interrupted-submit behavior so answers are neither lost after acknowledgement nor counted twice.
- O5 — The application is accessible as a responsive web page and deployable using Docker. Public access uses TLS; an explicitly configured local-network deployment may use HTTP.
- O6 — A later PWA slice supports installation on a phone and connected use. Offline exercise execution and deferred synchronization are not required. The design distinguishes PWA secure-origin requirements from ordinary LAN HTTP access.
- O7 — Arithmetic generation/checking remains deterministic; Student Model remains independent of policy. Rules constrain adaptive decisions, GPU Framework provides Laya inference, and unavailable or invalid inference leaves rules-based play available. Fixed mode also respects safety constraints without policy-driven difficulty changes.
- O8 — The owner receives a technology decision, child-navigation design, documented integration boundaries and ordered vertical slices. Every slice states its user-visible result, dependencies, acceptance scenarios and verification approach; every source capability is retained or explicitly scheduled in a later slice.

- Done when: the owner can review an English design and ordered slice plan with all O1–O8 outcomes mapped to acceptance scenarios, all eight ADRs and HLD/LLD capabilities accounted for, and unresolved external dependencies explicitly identified with activation checkpoints.
- Done when: design and plan pass their applicable chain checks and approved scope is reflected in mmath wiki with a clean task-page lint result; no application-runtime success is claimed from document review.

## 3. Technology and Deployment Boundaries

| Layer | Selection | Responsibility |
|---|---|---|
| Browser | React, TypeScript strict mode, Vite, React Router declarative mode | Screens, navigation, input and request lifecycle |
| Styling | CSS Modules, CSS custom properties, local SVG assets | Responsive child interface, focus and reduced-motion styles |
| Browser state | Component state and a session reducer; native fetch through one typed API client | Draft answer, pending request, server snapshot; no Redux initially |
| API | Python, FastAPI, Pydantic, Uvicorn | Validated API, authorization and game orchestration |
| Persistence | PostgreSQL 17 baseline from LLD, SQLAlchemy 2 async sessions, psycopg, Alembic | Transactions, explicit migrations and durable state |
| Inference client | HTTPX AsyncClient | Bounded calls to GPU Framework; no browser credential |
| Passwords | Argon2id through a maintained password hashing library | Password verification and parameter upgrades |
| Edge | Caddy | Static assets, API proxy, public TLS or explicit LAN HTTP |
| Tests | pytest with real PostgreSQL integration tests; Vitest/Testing Library; Playwright | Domain, integrity, component and browser acceptance |
| Packaging | Docker Compose, npm lockfile and Python dependency lockfile | Reproducible build and deployment |

Select supported compatible patch versions and pin lockfiles and container digests during the first implementation slice. Do not introduce floating production tags. This design selects technology families rather than inventing unverified future versions. Node is a build/development dependency; production frontend assets are served by Caddy. Vite preview is not the production server.

Runtime containers: `web`, `api`, `postgres`. A one-shot `migrate` service completes before API readiness. PostgreSQL and API ports are internal to Compose; only the edge is published. PostgreSQL data and Caddy certificate state use named volumes. No Redis, queue worker, bundled Laya, Prometheus or Grafana is required for the initial release.

Same-origin `/api/v1/*` routes to FastAPI; asset and SPA routes go to the frontend. Unknown API paths return API errors and never fall through to the SPA. Development uses the Vite API proxy. Production does not enable wildcard credentialed CORS.

## 4. Child and Parent Experience

Product copy is Russian. Documentation and code comments remain English. Screen names below describe the UI rather than literal copy.

| Screen | Primary action | Secondary actions / state |
|---|---|---|
| Parent sign-in/register | Sign in / create account | Validation and generic credential errors |
| Child selector | Select avatar/name | Parent area; add first child when empty |
| Child home | Resume if unfinished, otherwise Start | Own progress; switch child |
| Exercise | Submit answer | Hint, erase digit, pause/leave |
| Feedback | Continue | Visual explanation for errors; no automatic timed dismissal |
| Session summary | Return home | Completed tasks, learned skills and encouraging feedback |
| Child progress | Return to child home | Recent sessions and skill progress without rankings |
| Parent area | Save profile settings | Switch profiles, account sign-out |

Use one arithmetic task at a time. The numeric keypad and physical keyboard both work. Keep the expression, entered answer, hint and primary action visible at 320 CSS-pixel width without horizontal scrolling. Interactive child controls are at least 48 by 48 CSS pixels, with visible focus. Color is accompanied by text/icon feedback; normal text contrast is at least 4.5:1. Respect reduced motion and retain usable layout at 200% zoom. Feedback is announced through an accessible live region; navigation moves focus to the new screen heading or answer control.

For younger children, support counters, ten-frames and number-line explanations; older children use the same navigation with less visual scaffolding. Hints are available rather than forced by age. Do not use countdown pressure, punishment for mistakes, leaderboards, streak-loss penalties or a free-form AI chat. Initial visual style: warm neutral background, high-contrast arithmetic, restrained accent colors and short CSS transitions. Final illustration details can evolve without changing navigation contracts.

Parent settings require recent password confirmation before mutation, even when a child is playing within the parent's authenticated browser. This is a product separation aid, not a claim of isolation against a child who knows the parent's password. Child selection does not change the server account identity.

Disconnected state preserves the visible exercise and draft answer, disables progression and explains that connection is needed. An ambiguous submission displays a retry/reconcile action, not an unverified success. A page refresh reloads server state; unsubmitted digits are not part of the durable-progress promise.

Acceptance UX-01: a walkthrough at 320, 768 and 1280 CSS pixels covers start, answer, hint, feedback, leave and resume using touch and keyboard. UX-02: manual review confirms labels, focus, contrast and reduced motion. UX-03: before public release, a supervised formative test includes the younger and older ends of the target range; inability to identify the next action is a design finding, not proof that the child lacks arithmetic ability.

## 5. Child Profiles and Difficulty

| Setting | Rule / initial default |
|---|---|
| Display name and avatar | Local non-identifying avatar set; no photo upload |
| Age | Whole years 5–10; store age band/configuration rather than full birth date |
| Mode | `automatic` default or `fixed` |
| Topics | Addition/subtraction initially; multiplication is selectable; at least one topic |
| Difficulty band | Integer 0–4; starting band in automatic, maintained band in fixed |
| Session length | Parent selects 5, 10 or 15 active minutes; default 10 |

Suggested initial bands are 0 for ages 5–6, 1 for 7–8 and 2 for 9–10. These are editable onboarding defaults, not a diagnosis or a restriction on ability. Automatic progress is skill-specific and persists across sessions. The initial band is used for an unpracticed skill; it does not reset learned progress every login.

Profile changes take effect at the next new session. An existing session keeps an immutable settings snapshot, shown when the parent chooses to resume it. To apply changes immediately, the parent explicitly finishes that session and starts a new one. No hidden rewriting of an active exercise.

Automatic policy may repeat, reduce/increase a band, switch eligible skills or select hint behavior. Increase by at most one band at a time. Three consecutive errors forbid an increase and select an easier eligible band. Five consecutive correct unhinted answers allow an increase. A hinted answer does not contribute to a promotion streak. At the easiest band, repeat with a visual hint; at the highest, repeat or switch. All actions remain within enabled topics and supported bands.

Fixed mode locks the difficulty band. Policy cannot choose `harder` or `easier`; it can repeat, switch to an enabled skill at that band and recommend a hint. Statistics and mastery continue to update. A failed answer does not silently change the fixed setting. A session limit ends the session; it does not generate more work at a lower band.

Acceptance MODE-01: a new child defaults to automatic. MODE-02: a fixed-band session retains its band through successes, failures, hints and reconnects. MODE-03: automatic promotion never occurs after the error threshold, and boundaries are enforced before and after policy selection. MODE-04: changing the profile cannot alter an already-issued problem.

## 6. Deterministic Mathematics and Student Model

The initial skill catalogue preserves addition within 10/20, subtraction within 10/20, doubles, near-doubles, make-ten and multiplication by 2/3; the upper addition/subtraction range reaches 50 as in LLD. These skills may be introduced in successive slices but must all have a named delivery slice. General multiplication can extend to tables 2–10 within the same catalogue design. Division and negative-number exercises are not part of this baseline.

Each catalogue entry defines eligible bands, operand/result bounds, operation, generator and deterministic hint renderer. The generator selects only from entries eligible for the session. Examples anchoring the shared bands: addition band 0 uses operands 0–5, band 1 result at most 10, band 2 bridging ten within 20, band 3 general results within 20, band 4 results within 50. Subtraction mirrors result/operand ranges with nonnegative answers; band 2 crosses ten. Specialized patterns such as make-ten declare their supported bands rather than pretending that every skill has five meaningful levels. Fixed mode excludes unsupported skill/band pairs, and invalid profile combinations are rejected with selectable valid alternatives.

The backend alone computes correct answers. Browser payloads never contain `correct_answer` before submission. One graded answer is allowed for each issued problem; mistakes lead to feedback and a subsequent exercise. Error classification preserves `off_by_one`, `concatenation`, `subtraction_confusion`, plus `other`; ties use that listed priority after checking correctness. Applicable operations are explicitly checked to avoid classifying a valid alternate operation by accident.

Maintain lifetime attempts/accuracy and recent windows of 5 and 20 attempts per skill. Mastery starts as unknown until an attempt exists; UI reports learning progress rather than a clinical measure. Retain the LLD starting formula: 0.50 recent accuracy + 0.30 speed score + 0.20 consistency, clamped to [0,1]. For the initial implementation, recent accuracy uses up to 20 attempts; consistency is the fraction of those attempts that are correct without hints; speed score is min(1, target/mean active response time on correct unhinted attempts), or 0 when none exist. Target is 10 seconds initially and versioned with the formula. Policy promotion requires the accuracy/streak gates even if speed score is high. These are explicit initial heuristics, subject to later evidence-based calibration.

The browser measures active visible response time, excluding hidden/paused/request-wait intervals. It reports the sample as untrusted telemetry, validated for nonnegative bounded values against server timestamps. Missing or implausible samples are excluded from speed calculations; they never invalidate an otherwise valid arithmetic answer. Browser timing cannot determine ownership, correctness or grant permissions.

Acceptance MATH-01: property tests cover every delivered skill/band and numeric bound. STUDENT-01: a known attempt sequence yields exact aggregates and reproducible mastery independent of Laya availability. STUDENT-02: invalid timing samples cannot trigger promotion through the speed term.

## 7. Accounts and Security Boundary

One parent account owns multiple child profiles. All child, session, attempt and progress queries derive ownership from the authenticated account; an identifier supplied by the browser never authorizes access. Unknown and other-family resources have the same not-found behavior. Data integrity tests use two parents with similarly named children.

Use opaque random server sessions stored as hashes in PostgreSQL. Cookies are HttpOnly, SameSite=Lax, Path=/ and Secure in public mode, without a Domain attribute. Rotate sessions on login and revoke on logout. Proposed initial expiry is 30 days absolute; parent-setting mutations require password confirmation within the last 10 minutes. Passwords use Argon2id; accept long passphrases and cap inputs before expensive hashing. Apply account/IP login throttles without permanently locking a victim account.

Mutating routes validate the configured same-origin Origin and a session-bound CSRF token; login/register forms use a pre-authentication CSRF context as well. GET never changes game state. Do not store authentication or Framework bearer tokens in localStorage. Responses containing personal or game state use `Cache-Control: no-store`; logs exclude passwords, cookies, tokens and answer-bearing request bodies.

Public email is a login identifier in the initial design, not a verified claim of mailbox ownership. Public release must explicitly communicate this limitation; email ownership verification and self-service password-reset delivery are a separate account-lifecycle decision, not an assumed SMTP dependency. A deployment-local operator reset command with explicit account selection and session revocation is the initial recovery path; it is not exposed over the web. Its use is operator-authorized, audited without secrets and tested on synthetic accounts. No routine operator access to child answers is added by this design.

Local HTTP uses the same account model and CSRF checks, but cannot use Secure cookies and does not protect credentials on the wire. It is an explicit `lan-http` deployment setting, never an automatic fallback from failed TLS. Do not expose this mode to the internet. Public mode rejects an HTTP application origin. Trust forwarded headers only from the configured reverse proxy and require the canonical Host/origin.

Acceptance AUTH-01: register, sign in, expire, revoke and recover a synthetic account. AUTH-02: cross-family resource access, missing/invalid CSRF and forged ownership are rejected. AUTH-03: public cookies are Secure; local HTTP is enabled only by the explicit deployment mode. AUTH-04: built frontend assets and logs contain no credential values. Public release includes review of the documented email-recovery limitation.

## 8. Durable Game State and Resume

Separate the authentication session from the learning session. At most one unfinished learning session exists per child; a database partial unique index enforces this. Different children can play concurrently. Multiple browsers using the same child reconcile to the same server-owned learning session.

| Entity | Additions beyond source LLD |
|---|---|
| account / auth_session | Email identity, password hash, hashed session identifier, expiry and revocation |
| player | Account FK, display settings, mode/band/topics/session-duration configuration |
| player_skill | Lifetime and recent aggregates, current automatic band, mastery/formula version |
| session | Player FK, settings snapshot, state/phase, version, current problem, pending next problem, feedback and active time |
| problem | Session FK, ordinal, skill/band/operands, server-only answer, issued time and hint state |
| attempt | Unique session/problem, request id, request fingerprint, submitted answer, result, timing and hint-used flag |
| policy_decision | Attempt FK, mode, allowed actions, state, provider/version, proposed/applied decision, latency, fallback reason and outcome aggregates |

Foreign keys and ownership checks connect every problem and attempt to its learning session and child. State is `active` or `finished`; active phase is `answer` or `feedback`. Pausing/leaving preserves active state; it does not create a second unfinished session. No special Redis state is authoritative.

An accepted answer and its consequences are one database transaction: lock the child row, validate ownership/session version and issued problem, deduplicate, write the attempt, update Student Model, choose/validate policy, persist feedback and the next problem (unless finishing), and advance session version. Return success only after commit. PostgreSQL row locking and unique constraints enforce the same rule across API workers; an in-process mutex is insufficient.

For the initial single-family-oriented deployment, a Framework call may occur inside that child-scoped transaction with a hard 350 ms total client deadline and no retry. This deliberately favors one simple atomic commit over a multi-stage queue. It temporarily serializes requests for that child only; unrelated children continue. Pool wait, connection and response time all count toward the deadline. Fallback must fit within the inherited 500 ms policy target; end-to-end performance is measured rather than inferred. If measured contention violates acceptance, redesign this boundary before release instead of increasing the timeout silently.

Every answer POST supplies a generated `submission_id`, `problem_id`, integer answer, response-time sample and `expected_version`. The same identifier and fingerprint replay the stored attempt result without reapplying mastery or policy. Reuse with different content returns 409. A different identifier for an already answered problem also returns 409 with a current snapshot. Replay authorization is checked before deduplication. A replay returns the immutable result plus the latest session snapshot; the client never overwrites a newer snapshot with an older version.

The answer response leaves the session in feedback phase with its saved explanation and an already-persisted next problem. `advance` moves to that next problem, sets its active start time and increments the version; repeated advance for the same completed attempt is a no-op returning current state. Generating a pending problem does not start response-time measurement. On the final attempt, feedback remains available and advance finishes the session. Refresh during feedback restores it, not a second grading opportunity.

Client retains the pending submission id/body in tab-scoped sessionStorage until acknowledgement, allowing refresh and retry of an ambiguous in-flight request. This small retry record is not an offline attempt queue; it contains no credentials and is cleared on logout or profile switch. After a full browser close, the server snapshot remains authoritative. An uncommitted answer may need re-entry, while committed answers are never lost or counted twice.

Hint exposure is persisted through an idempotent hint endpoint under the same child lock and version discipline before returning hint content. Repeated requests do not increment hint usage twice. Profile mutation, session creation, finishing and advancing acquire the same child-first lock order. Response-time measurement after reload excludes absent time; missing timing does not prevent resume.

Session time is accumulated from bounded active foreground intervals, not from time since account login. The server also enforces expiry/limits at state transitions. When the configured active duration is reached, finish after the current graded task and feedback; do not create a further problem. An explicit Finish action is always available and preserves prior attempts.

Acceptance RESUME-01: refresh in answer and feedback phases restores the correct phase/problem. RESUME-02: drop the response after commit and retry; one attempt, mastery update and applied decision exist. RESUME-03: crash before commit leaves none of those changes. RESUME-04: simultaneous answers from two browsers produce one accepted attempt; the stale browser reconciles. RESUME-05: restart containers with existing database volume and recover history/current position. RESUME-06: two children do not share locks or progress.

## 9. API Surface

All routes use `/api/v1`; bodies and errors are generated from Pydantic/OpenAPI contracts. The frontend's TypeScript contract is generated or checked against that schema during build verification. Browser correctness is not a substitute for server validation.

| Operation | Purpose / success behavior |
|---|---|
| POST /auth/register, /auth/login, /auth/logout | Establish/revoke account session; CSRF-protected |
| GET /auth/session | Account session summary and CSRF bootstrap, no credential disclosure |
| POST /auth/confirm-password | Short-lived permission to change parent settings |
| GET/POST /players; GET/PATCH /players/{id} | Own profiles and validated configuration |
| GET /players/{id}/progress | Skill summary and paginated session history |
| POST /sessions | Retain LLD player_id; use profile mode rather than trusting an arbitrary mode override; return existing active session or atomically create one |
| GET /sessions/{id} | Current versioned phase/problem/feedback snapshot |
| POST /sessions/{id}/attempts | Atomic graded submission with deduplication |
| POST /sessions/{id}/hint | Persist and return deterministic visual hint |
| POST /sessions/{id}/advance | Acknowledge saved feedback and reveal pending next task |
| POST /sessions/{id}/finish | Idempotent finish preserving saved work |

LLD `mode: adaptive` is normalized to profile `automatic` for the documented legacy example; incompatible overrides are rejected, not silently applied. There is no deployed existing client, so the reviewed profile-based contract is authoritative for implementation. Existing `problem_id`, `answer`, `response_ms`, `correct`, `feedback` and `next_problem` concepts are preserved. `next_problem` is not shown until advance. Lifecycle fields explain terminal sessions where it is null.

Errors use a stable code and safe message: 401 session expired, 403 forbidden action/CSRF, 404 resource unavailable, 409 version/idempotency conflict, 422 invalid input, 429 throttled, 503 application/database unavailable. Inference failure alone produces a successful rules-based answer response and internal fallback evidence, not a child-facing 503.

Acceptance API-01: contract tests cover success and listed failure paths. API-02: no GET mutates learning state and responses never leak another family's identifiers or a pending problem's answer.

## 10. GPU Framework and Policy Evolution

Configuration consists of server-only Framework base URL, the separately verified Laya route/model identity and a token file when the selected Framework access boundary requires one. Public Framework calls use TLS and its documented bearer token. Reviewed direct-LAN access may omit a token according to Framework policy; mmath does not invent new token scopes. Read the secret from a mounted file, not a Vite environment variable. Forward neither the parent's cookie nor account credentials.

The transport adapter accepts a compact policy state and allowed actions, and returns a typed policy proposal with model/version provenance, probabilities/confidence when actually supported, and bounded diagnostics. It never calls Framework runtime switch/load/stop endpoints. No public Laya endpoint or confidence schema is invented: the assessed native `POST /v1/systemone` is not evidence that Framework publishes that route.

The Framework activation checkpoint requires its owner to provide the reviewed route, authentication mode, model identifier/version, schema, confidence semantics, error taxonomy and an operator-controlled privacy boundary. Backend tests use a fake transport until this contract exists. If verified confidence is absent, shadow evaluation is permitted but active Laya promotion is not.

Newer evidence from `framework/reference/tasks/laya-system-one-integration` records an approved integration design and repository Tasks 1–2 completed, with Task 3 next. It does not establish live publication. Its decision history specifies Runtime Manager ownership, separate System One discovery, payload-free gateway audit and single-flight inference with immediate 429 backpressure. mmath treats this 429 as a recorded fallback without queueing or retrying. The earlier feasibility assessment in the approved intent remains historical context; the integration task is the current dependency authority. No Framework API is activated by this design.

Deployment policy modes are `rules`, `shadow`, `active`; this is independent of each child's automatic/fixed difficulty mode. Default is `rules`. Shadow records the model proposal but always applies the rule decision. Active applies a legal proposal only after schema, confidence and constraint checks; otherwise it applies fallback. Initial active confidence threshold is 0.8 only after probability semantics are verified and calibrated offline; it is a proposed rollout value, not a claim about current Laya output quality.

Retain the small action space `repeat`, `easier`, `harder`, `switch`, `hint`, `no_hint`. A difficulty action changes the next task band, switch selects an eligible skill at its lawful band, hint selects the next task's visual support and no_hint removes automatic support while leaving the child's hint button available. Required corrective explanations are not suppressed. The deterministic constraint engine normalizes every proposal; an illegal action becomes a logged fallback. At fixed mode, harder/easier are not offered and cannot pass post-validation.

Every applied transition stores policy state, allowed actions, policy mode, model/version if contacted, proposal or sanitized failure, actual action, latency and fallback reason. Rules-only transitions are also recorded. Only committed transitions update training outcome aggregates; retries do not duplicate learning evidence. Retain next-five accuracy/time, session completion and later-return signals with incomplete outcomes explicitly marked. Export is operator-triggered and pseudonymous; raw emails/names and secret headers are excluded.

Stages retain source evolution: V0 rules; V1 shadow; V2 confidence/constraint-gated Laya; V3 offline evaluation, calibration and a future fine-tuned model supplied by Framework. Export and evaluation preparation belong to mmath; model training and runtime activation remain Framework/operator work. A future A/B comparison needs a separate reviewed experiment decision before assigning children to cohorts.

Acceptance POLICY-01: timeout, HTTP failure, malformed/oversized response, illegal action and low confidence all result in legal fallback. POLICY-02: shadow never changes the rule result. POLICY-03: active cannot bypass fixed mode or error-streak limits. POLICY-04: no personal identifiers or credentials reach inference state/logs. POLICY-05: model unavailability does not prevent startup/readiness or play in rules mode.

## 11. Operations, TLS and PWA

Docker Compose has explicit `public` and `lan-http` configuration overlays. Public mode requires a canonical HTTPS origin and DNS/certificate prerequisites; Caddy handles TLS and HTTP redirection. LAN HTTP binds to the operator-selected LAN address with deployment guidance against WAN exposure. No mode is selected by guessing the client's IP. The deployment guide states that HTTP credentials and content are visible to network observers.

Migrations run once before API readiness, not from every request worker. A migration failure prevents readiness without destroying the database volume. `/health/live` checks process liveness; `/health/ready` checks database connectivity and schema compatibility. Framework status is diagnostic and does not gate rules-based readiness. `docker compose down` without volume deletion must preserve accounts and progress.

Document backup and restore using PostgreSQL tools, including a verification procedure that restores a synthetic account/history/current session into a separate database. A backup is not considered validated merely because an archive exists. No automatic retention deletion of child history is introduced in this scope.

Metrics preserve policy latency/errors/fallbacks, attempts/correct ratio, session duration and mastery changes. Structured logs use pseudonymous session/player ids and policy metadata, excluding secrets, email and answer-bearing payloads. Keep high-cardinality identifiers out of metric labels. Applied policy state belongs in PostgreSQL audit records rather than ordinary console logs. Prometheus/Grafana and Redis remain optional future deployment additions.

The later PWA slice adds a manifest, local icons, standalone display and a minimal service worker caching only versioned public shell assets plus a connection-required screen. Do not cache `/api`, auth responses or personalized navigation data. No background answer submission or offline game queue. Avoid applying a waiting frontend update mid-answer; offer reload at a safe screen. Installation is tested on supported Android Chromium and iOS Safari flows; platform-specific install instructions are shown only when applicable. LAN HTTP retains the ordinary website; LAN installation requires separately provisioned trusted HTTPS.

Acceptance OPS-01: clean Compose deployment, migration failure, restart and restore drills are documented/tested. OPS-02: public HTTP redirects to HTTPS and backend/database ports are not exposed. PWA-01: install, launch, reconnect and logout work on the target browsers; offline launch explains connection need and exposes no previous child's cached content.

## 12. Vertical Slice Map

These slices describe design boundaries, not an approved implementation plan. Each implementation task will name exact files, commands and executable acceptance checks after spec approval. Shared setup is included in the first slice that needs it.

| Slice / topic suffix | User-visible result | Dependencies | Acceptance / verification |
|---|---|---|---|
| S1 family-first-session | Parent registers, creates a child and completes a short fixed-band addition session; history survives restart | None; includes Compose skeleton, DB migrations, auth, React navigation and minimal game | AUTH-01/02, MATH-01 initial skill, RESUME-02/03/05; real PostgreSQL + Playwright |
| S2 resume-and-child-navigation | Child resumes exact answer/feedback phase; parent can manage multiple children; hints and accessible keypad work | S1 | UX-01/02, RESUME-01/04/06, ownership races, hint retries and settings snapshot tests |
| S3 adaptive-skill-practice | Automatic default adjusts skill-specific difficulty; fixed option remains stable; complete baseline skill catalogue and progress summary | S2 | MODE-01–04, MATH-01 all baseline skills, STUDENT-01/02; deterministic sequence/property tests |
| S4 public-docker-release | Parent uses the site through TLS; operator can deploy LAN HTTP explicitly and restore a backup | S3 | AUTH-03/04, OPS-01/02, UX-03; public-mode security and restore checks; credential-recovery limitation reviewed |
| S5 framework-shadow-policy | Gameplay remains rules-based while real Framework Laya proposals are captured for comparison | S3; actual integration requires Framework contract checkpoint | POLICY-01/02/04/05, fake transport suite plus authorized live contract smoke |
| S6 guarded-adaptive-policy | Evaluated Laya decisions can influence eligible automatic-mode sessions, with fallback | S5; calibrated confidence and rollout review | POLICY-01/03, measured latency, fixed-mode invariance, offline evaluation and operator rollback |
| S7 connected-mobile-pwa | Existing online game installs and opens on phone | S4 | PWA-01; Android/iOS installation and no-personal-data-cache review |
| S8 policy-learning-evidence | Operator exports pseudonymous decision/outcome data and compares candidate policies offline | S5; candidate training supplied by Framework | Export schema, outcome completeness, no secret/PII fields, deterministic evaluation; V3 training/experiment activation remain external checkpoints |

Suggested delivery order: S1 → S2 → S3 → S4, then S7 for the mobile installation objective. S5 can follow S3 when Framework is ready; S6 and S8 follow its evidence. S4 is the first public release checkpoint; prior slices are development/LAN acceptance increments. The final S3 state defaults to automatic; S1's fixed-band exercise is a bounded intermediate increment, not the product default.

Keep one canonical parent topic `mental-math-web-platform` for this design chain. Slice names are logical identifiers, not new task pages or branches created by this document. Execution may later create separately authorized child topics with explicit linkage; no conflicting artifacts are created now.

## 13. Source Coverage and Explicit Reconciliation

| Source | Design preservation | Slices |
|---|---|---|
| ADR-001 deterministic math / separated responsibilities | Sections 3, 6, 8, 10 | S1–S3, S5 |
| ADR-002 local inference and privacy | Operator-controlled Framework boundary; browser cannot access token; replaces bundled process only | S5–S6 |
| ADR-003 Rules + Laya, safety/fallback | Pre/post constraints and rules availability, including fixed mode | S3, S5–S6 |
| ADR-004 shadow then training/evaluation | Explicit V0–V3 evolution and operator experiment checkpoint | S5–S6, S8 |
| ADR-005 independent Student Model | Versioned deterministic aggregates/formula | S3 |
| ADR-006 bounded actions | Six action semantics and legal-set filtering | S3, S5–S6 |
| ADR-007 Python/FastAPI | Selected backend | S1 |
| ADR-008 all policy decisions | Durable committed state/proposal/applied/outcome audit | S3, S5–S6, S8 |
| HLD game flow, skills, persistence | Transactional game flow, full baseline catalogue, PostgreSQL | S1–S3 |
| HLD latency/reliability/observability | Measured targets, deadlines, fallback and named metrics | S4–S6 |
| HLD Docker and optional services | Three required containers; external Framework; optional Redis/monitoring deferred | S1, S4 |
| HLD REST/WebSocket | REST selected for discrete exercises; WebSocket unnecessary for the described flow | S1–S3 |
| LLD generator, difficulty, errors, mastery | Sections 5–6; specialization eligibility and deterministic arithmetic | S1–S3 |
| LLD policy state/adapter/constraints/fallback | Section 10; verified Framework transport replaces conceptual native request | S3, S5–S6 |
| LLD API examples | Section 9 retains concepts; adds account ownership, versions, hint/advance/resume | S1–S3 |
| LLD tables and Compose | Section 8 additive ownership/session fields; Section 11 deployment | S1–S4 |
| LLD training rows and reward | Decision/outcome export; retain 0.40 accuracy improvement + 0.25 speed improvement + 0.20 completion + 0.15 retention as an evaluation candidate, not a live optimizer | S8 |

Existing ADR/HLD/LLD remain the historical baseline while this design is draft. The approved intent explicitly authorizes external Framework deployment instead of a bundled Laya container and adds account/PWA/mode/resume requirements. After checked-spec approval, update baseline deployment/API sections or add clear supersession links; do not silently rewrite accepted history during drafting.

## 14. Verification and Review Gates

| Intent | Concrete design proof / later execution evidence |
|---|---|
| O1 | Sections 5, 7–9; AUTH checks and two-family ownership tests |
| O2 | Section 4; touch/keyboard, visual accessibility and supervised usability review |
| O3 | Sections 5–6, 10; automatic/fixed mode sequence tests |
| O4 | Sections 8–9; real-DB races, response-loss/restart/rollback tests |
| O5 | Sections 3, 11; Compose/TLS/LAN/backup checks |
| O6 | Section 11; installation and connected-only behavior on target browsers |
| O7 | Sections 6, 10; deterministic math and policy failure/constraint tests |
| O8 | Sections 12–14; full source/outcome-to-slice coverage and later exact task plan |

Use real PostgreSQL for locking, partial uniqueness and migration tests; SQLite substitutes do not prove these invariants. Test failure windows before and after transaction commit, not just a successful button click. Domain/property tests cover bounds and arithmetic; frontend tests cover accessible states and pending/retry behavior; browser tests cover complete parent/child journeys. Framework contract tests distinguish fake transport from authorized live evidence.

During implementation, run focused checks per changed boundary and one full relevant suite on the final stable fingerprint, then reuse that evidence until inputs change. During this design-only stage, run document structure, coverage, hash/link and wiki lint checks; no application tests exist and no runtime result is claimed.

Human checkpoints: checked-spec approval before detailed plan; checked-plan approval before any execution; explicit public deployment authorization; Framework contract/activation and calibrated active-policy rollout; later training/experimentation decisions. These checkpoints do not prevent independent rules-based slices from being specified.

Remaining external dependency: Framework has no confirmed published Laya route in the reviewed evidence. The design does not resolve this by accessing credentials or activating models. Decision requiring explicit attention at spec review: initial account recovery is operator-assisted and email ownership is not verified; adding email verification/reset would introduce an SMTP/mail-delivery requirement.

## 15. Primary References

The following primary sources support technology behavior, not project-specific policy choices or measured performance claims.

- [React with TypeScript](https://react.dev/learn/typescript)
- [Vite production build](https://vite.dev/guide/build) and [static deployment](https://vite.dev/guide/static-deploy)
- [React Router modes](https://reactrouter.com/start/modes)
- [FastAPI Docker deployment](https://fastapi.tiangolo.com/deployment/docker/)
- [SQLAlchemy session isolation](https://docs.sqlalchemy.org/en/20/orm/session_basics.html)
- [PostgreSQL 17 row locking](https://www.postgresql.org/docs/17/explicit-locking.html)
- [HTTPX client](https://www.python-httpx.org/)
- [Caddy automatic HTTPS](https://caddyserver.com/docs/automatic-https)
- [OWASP session management](https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html), [password storage](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html) and [CSRF prevention](https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html)
- [W3C target-size guidance](https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum)
- [MDN PWA installation](https://developer.mozilla.org/en-US/docs/Web/Progressive_web_apps/Guides/Making_PWAs_installable) and [offline/background operation](https://developer.mozilla.org/en-US/docs/Web/Progressive_web_apps/Guides/Offline_and_background_operation)
