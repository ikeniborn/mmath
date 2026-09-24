---
topic: mental-math-web-platform
workflow:
  route: chain
  continuation: full
review:
  intent_hash: 1e77a63f4c624d1c
  last_run: 2026-09-24
  phases:
    structure: { status: passed }
    completeness: { status: passed }
    clarity: { status: passed }
    consistency: { status: passed }
    alignment: { status: passed }
  findings: []
---
# Intent: mental-math-web-platform

**Date:** 2026-09-24
**Status:** approved

## Objective

Turn the existing Mental Math ADR, HLD and LLD into a coherent web-platform design and an ordered set of vertical implementation slices. Select the technology stack and define a child-facing experience for ages 5–10 while preserving the documented arithmetic, student-model and adaptive-policy capabilities.

The current deliverable is design and implementation planning, not a deployed application. Product outcomes below are acceptance targets for the later implementation; this task must map each outcome to a design decision, slice and verification scenario.

Source baseline: [ADR](../../mental-math-adr.md), [HLD](../../mental-math-hld.md), [LLD](../../mental-math-lld.md), plus the user's subsequent decisions recorded in the mmath task ledger.

## Desired Outcomes

- O1 — A parent can register and sign in using email and password, select a child profile and access only their family's progress. Each child has independent settings, skills and history.
- O2 — A child aged 5–10 can identify how to start or resume a session, understand the current exercise, enter an answer and understand feedback. The design names these screens, primary actions and age-appropriate visual aids.
- O3 — Automatic difficulty is the default profile mode. Difficulty responds to the child's performance within profile settings and domain constraints. The parent can instead select fixed mode with a chosen difficulty; results continue to update history and the Student Model without automatic difficulty changes.
- O4 — Returning after closing the browser or restarting the application service preserves committed progress and offers continuation from the saved session position. The design specifies the authoritative saved state and interrupted-submit behavior so answers are neither lost after acknowledgement nor counted twice.
- O5 — The application is accessible as a responsive web page and deployable using Docker. Public access uses TLS; an explicitly configured local-network deployment may use HTTP.
- O6 — A later PWA slice supports installation on a phone and connected use. Offline exercise execution and deferred synchronization are not required. The design distinguishes PWA secure-origin requirements from ordinary LAN HTTP access.
- O7 — Arithmetic generation/checking remains deterministic; Student Model remains independent of policy. Rules constrain adaptive decisions, GPU Framework provides Laya inference, and unavailable or invalid inference leaves rules-based play available. Fixed mode also respects safety constraints without policy-driven difficulty changes.
- O8 — The owner receives a technology decision, child-navigation design, documented integration boundaries and ordered vertical slices. Every slice states its user-visible result, dependencies, acceptance scenarios and verification approach; every source capability is retained or explicitly scheduled in a later slice.

## Health Metrics

- Requirement coverage: all eight ADR decisions and the capabilities described in HLD/LLD have a traceable design/slice disposition; no silent removals.
- Arithmetic correctness: the design assigns zero answer-checking decisions to probabilistic inference.
- Progress integrity: acceptance scenarios require zero duplicate accepted attempts and zero loss of acknowledged attempts across retry/restart scenarios.
- Account isolation: acceptance scenarios require zero cross-family reads or writes; each child retains separate progress.
- Mode integrity: automatic is the default; fixed-mode acceptance scenarios require zero automatic difficulty changes.
- Reliability: inference timeout, invalid output and unavailability have a specified constrained fallback outcome; normal play does not depend on Framework control-plane mutations.
- Latency: retain HLD's policy-decision target of at most 500 ms on CPU and its desirable 100 ms GPU target; design distinguishes inference time from complete browser round-trip time. Runtime achievement is not claimed during planning.
- Privacy: child history and skill profiles remain in the operator-controlled deployment boundary; no external AI API receives them. Framework credentials never enter frontend assets or browser requests.

## Strategic Context

- Interacts with: children aged 5–10, parents, deployment operator, React web client, FastAPI Game API, Math Engine, Game Engine, Student Model, Constraint Engine, adaptive/fallback policies, PostgreSQL and GPU Framework API.
- Priority trade-off: proposed for approval — trust in arithmetic/progress and clear child interaction take priority; keep development and operation small within those constraints. The user selected React + TypeScript for visual development and growth after evaluating HTMX.
- Confirmed frontend direction: React + TypeScript, with Vite as the proposed build tool. Existing ADR-007 retains Python + FastAPI; HLD retains PostgreSQL.
- Framework evidence: `framework/architecture/framework-gpu-api` describes the gateway contract. `framework/reference/tasks/laya-gpu-deployment-feasibility` reports that Laya requires a new integration and was not installed at its recorded assessment. Native Laya `POST /v1/systemone` must not be assumed to be an available Framework public route.
- The original bundled Laya Compose example is superseded by the user's deployment boundary: mmath consumes GPU Framework API; Framework owns inference deployment. Route activation and Framework changes are a separate dependency, outside this task.

## Constraints

### Steering (behavioral guidance)

- Favor one clear primary action per child screen, large touch targets, visual explanations and short feedback. Keep parent configuration outside the exercise flow.
- Prefer the smallest set of frontend dependencies that supports the agreed experience; introduce additional state or UI libraries only for demonstrated requirements.
- Describe vertical slices by usable outcomes rather than dividing the work only into frontend/backend layers.
- Preserve source evolution from rules to shadow Laya, constrained active Laya and future fine-tuning; identify rollout prerequisites for each stage.
- Proposed profile controls for design review: age, allowed topics/operations, starting or fixed difficulty, session duration and automatic/fixed mode. The mode choices and automatic default are confirmed; exact ranges and configuration UX are design decisions.

### Hard (architectural enforcement)

- Retain React + TypeScript frontend, Python + FastAPI backend and PostgreSQL persistence. Application data and policy authority reside on the backend.
- Parent accounts use email/password; profiles and progress are separated by child and protected by account ownership.
- Support both automatic and fixed difficulty; automatic is the default. Fixed difficulty never bypasses allowed operations, numeric bounds or session limits.
- Use GPU Framework API for Laya with endpoint and credential supplied at deployment. Do not embed a Framework token in frontend code, generated assets, logs or repository files.
- Preserve deterministic mathematics, an independent Student Model, pre/post policy constraints, bounded action space, fallback, shadow evaluation and policy-decision history including state, model version, output, applied action and subsequent outcomes.
- Preserve the local/operator-controlled data boundary of ADR/HLD. Internet access to mmath does not authorize sending child information to third-party AI services.
- Docker deployment must distinguish public TLS access from optional LAN HTTP access. PWA installation and service-worker features require an appropriate secure origin.
- Do not implement offline gameplay, deferred client/server attempt synchronization, or Framework model lifecycle management in this scope.
- This task produces reviewable design and slices; application implementation, production deployment and Framework route activation require their own authorized execution step.

## Autonomy Zones

- Full autonomy (reversible, low risk): read source documents and authorized wiki pages, compare technologies, draft requirements and slices, and run documentation checks.
- Guarded (record evidence and assumptions): maintain the mmath task ledger and draft documents; reconcile source examples with explicit user decisions while preserving provenance.
- Proposal-first (needs approval): approve intent and detailed design, choose the chain continuation, change accepted functional contracts, expand scope or revise the data/privacy boundary. Unspecified profile controls remain proposals until design review.
- No autonomy (human only): expose public services, activate or modify GPU Framework deployments, alter domain grants, handle live credentials, perform destructive data operations or begin application implementation under this design-only task.

These zones describe the proposed task boundary for intent approval; they do not claim new approval for production operations.

## Stop Rules

- Halt if: a design would remove an ADR/HLD/LLD capability without an explicit user decision, expose a Framework credential, weaken account isolation, or require unapproved production changes.
- Escalate if: the actual Framework Laya contract or privacy boundary conflicts with the documented assumptions; mark the affected integration slice dependent on resolution while continuing independent design work.
- Done when: the owner can review an English design and ordered slice plan with all O1–O8 outcomes mapped to acceptance scenarios, all eight ADRs and HLD/LLD capabilities accounted for, and unresolved external dependencies explicitly identified with activation checkpoints.
- Done when: design and plan pass their applicable chain checks and approved scope is reflected in mmath wiki with a clean task-page lint result; no application-runtime success is claimed from document review.
- Human checkpoint: the draft intent must be checked before approval; detailed design and planning follow the accepted chain continuation. Completion of planning does not authorize application implementation.
