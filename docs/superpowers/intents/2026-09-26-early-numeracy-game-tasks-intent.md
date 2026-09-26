---
topic: early-numeracy-game-tasks
workflow:
  route: chain
  continuation: pending
review:
  intent_hash: 878235b74d165bf2
  last_run: 2026-09-26
  phases:
    structure: { status: passed }
    completeness: { status: passed }
    clarity: { status: passed }
    consistency: { status: passed }
    alignment: { status: passed }
  findings:
    - id: F-001
      phase: clarity
      severity: WARNING
      section: Health Metrics
      section_hash: 2e4a2d124ccec4c3
      fragment: "the frontend bundle grows by no more than the limit agreed in the design for the SVG object set"
      text: "The bundle-growth metric names no number; the threshold is deferred to the design."
      fix: "The design doc states the limit in kilobytes (gzip) and the measurement command."
      verdict: open
      verdict_at: null
    - id: F-002
      phase: clarity
      severity: WARNING
      section: Health Metrics
      section_hash: 2e4a2d124ccec4c3
      fragment: "Time to the first task on the LAN deployment is not worse than today"
      text: "No baseline value or measurement method is named for time to the first task."
      fix: "The design doc records the baseline measured on minipc and the measurement method."
      verdict: open
      verdict_at: null
---
# Intent: early-numeracy-game-tasks

**Date:** 2026-09-26
**Status:** approved

## Objective

A child aged 4–5 does not yet read numerals or task text, so the current tasks — bare numbers, a text prompt and a digit keypad — are both inaccessible and boring for them. The platform needs game-form tasks built from the objects of the child's theme: the child counts and compares pictures, answers by tapping a picture or the objects themselves, and hears the task spoken aloud. Beyond coping with tasks, the child should want to come back: a theme reward after every round and a visible collection carry the motivation that numerals cannot.

Why now: the platform is deployed on the LAN and its first real user is a four-year-old. The S18 study on the predecessor topic ([mental-math-web-platform](2026-09-24-mental-math-web-platform-intent.md)) showed that at band 0 a 4–5-year-old meets six skills, pictures cover three of them, and every answer still requires reading and typing numerals.

Scope chosen by the owner: all three tiers of the study. Tier A — visual layers on the existing band-0 skills (compare as two piles to tap, odd/even as pairing with one left over, neighbour-one as train carriages, missing addend as objects hidden behind a garage or house, subtraction as objects leaving), picture answer choices instead of the keypad, spoken prompts. Tier B — new task kinds: count objects, make the same number, quick-look subitizing with dice and domino patterns, what comes next (AB/ABB patterns), how many to five on a five-frame. Tier C — order towers by size, fair sharing to two animals, shapes and sizes. Cross-cutting — theme graphics beyond emoji (an SVG object set per theme with scenes), a round reward with a collection, round pacing for ages 4–5.

## Desired Outcomes

- O1 — A child aged 4–5 completes a round without reading and without the keypad: every task is spoken aloud, every task is shown with the objects of the child's theme, and every answer is given by tapping a picture, a card or the objects themselves.
- O2 — A round for a child aged 4–5 contains at least five distinct game forms (for example count, which has more, make the same, quick look, what comes next, who is in the garage), not a single form repeated ten times.
- O3 — After a round the child receives a reward of their theme and can see the collection of rewards earned so far.
- O4 — The parent sees the new early-numeracy skills in the progress view alongside the existing ones: counting, comparing groups, patterns, size and shape.
- O5 — A supervised check with a real four-year-old: the child finishes a round on their own and asks for another one.

## Health Metrics

- All 18 strict GWT scenarios of the mmath domain and every existing backend, frontend and end-to-end test stay green; the scenarios `task-shapes-solvable-from-public-prompt`, `automatic-band-promotion` and `idempotent-hint-exposure` are extended, never weakened.
- No public field, hint, picture or answer card carries the correct answer — for the existing kinds and for every new kind; the catalogue-wide leak test covers the new kinds.
- The experience of children aged 6–10 is unchanged: pictures, picture answers and speech apply only to profiles aged 5 and under; their tasks, prompts and keypad render byte-for-byte as before.
- Time to the first task on the LAN deployment is not worse than today, and the frontend bundle grows by no more than the limit agreed in the design for the SVG object set.
- The PWA offline behaviour is unchanged: the connection-required page, the cache allowlist and the never-intercepted `/api`, `/health` and `/internal` paths.

## Strategic Context

- Interacts with: the skill catalogue and generators (`backend/mental_math/game/catalogue.py`), the session engine with its atomic answer transaction and the public problem view (`engine.py`), the grader (`validator.py`), hints (`hints.py`), the rules/shadow/active policy and its legal action set, the frontend game feature (`GamePage`, `TaskPicture`, `ChoicePad`, `NumberPad`, `Hint`, themes and labels), the PWA shell and cache allowlist, the parent progress view, child profiles and themes, the LAN deployment on minipc, the ru/en localisation, and the people involved — the parent and the four-year-old child.
- Priority trade-off: trust. Correct grading, no answer leak and an unchanged experience for children aged 6–10 come before the breadth of the game set in the first release; a smaller verified set ships before a larger unverified one.

## Constraints

### Steering (behavioral guidance)

- Prefer a tap to a drag: every interaction should be answerable by tapping; drag is used only where tapping cannot express the action, and even then with a tap fallback.
- One mechanic per task: a task asks for one action (tap a pile, tap a card, tap objects to count), never a sequence of different gestures.
- Number ranges follow age: within 5 for a four-year-old, within 10 for a five-year-old.
- Rewards carry no timers, no streak pressure and no competition between children.
- Existing skill codes, topics and bands keep their names; new skills are added, not renamed.
- The picture stays decorative and the spoken prompt stays optional: the task text remains the accessible text and the task is solvable with sound off.

### Hard (architectural enforcement)

- The correct answer never reaches the client: not in the public problem, not in a hint, not in a picture, not in the answer cards, not in a timer payload. The quick-look timer is user-experience only; the server grades the answer as for any other kind.
- An issued problem is immutable; new kinds follow the same session, replay and resume contract as the existing ones.
- The server grades every kind, existing and new, from the stored problem; the client never decides correctness.
- Themes remain a free per-profile choice with no gender attribute.
- The policy (rules, shadow, active) chooses only from the legal action set; new kinds do not add actions to it.
- Russian and English localisation for every new string; strict GWT scenarios in the mmath domain for every new observable behaviour.
- No external CDN, font, script or asset: everything ships in the bundle. Assets are self-made or carry a licence that permits inclusion in the repository, recorded next to the asset.
- Speech uses only the browser speech synthesis API; no external text-to-speech service.
- No new data about the child is collected: no microphone, no camera, no recordings.

## Autonomy Zones

- Full autonomy (reversible, low risk): generators and tests for new skills; visual layers on existing skills; localisation strings; speech prompts; icon and colour choices inside a theme.
- Guarded (log + confidence threshold): new kinds in the `PublicProblem` contract and their GWT scenarios; migrations that add data without deleting any (rewards, new skills); bundle growth up to the agreed limit — each recorded in the task ledger.
- Proposal-first (needs approval): a new topic in the catalogue or a change to the progression rules; a change of the round length; any change to the experience of children aged 6–10; new npm dependencies; deployment to minipc.
- No autonomy (human only): the supervised check with a real child; merging the PR; buying or licensing assets.

> These zones OVERRIDE subagent-driven-development's "continuous execution,
> don't pause" default. Any task touching proposal-first / no-go decisions
> is marked HUMAN CHECKPOINT in the plan.

## Stop Rules

- Halt if: any answer leak is found in a public field, hint, picture or card, or any strict scenario of the predecessor topic turns red.
- Escalate if: a migration would need to delete or rewrite data, or the Framework policy contract (state, criteria, legal actions) would have to change.
- Done when: the five Desired Outcomes are observable on the LAN deployment — a 4–5-year-old profile plays a spoken, picture-only round with at least five game forms, receives a theme reward and sees the collection, the parent sees the new skills in progress — and the supervised check with the real four-year-old (O5) has been performed and recorded in the task ledger.
