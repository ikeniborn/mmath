---
topic: early-numeracy-game-tasks
review:
  spec_hash: 33cbdd0d2824a6e9
  last_run: 2026-09-26
  phases:
    structure: { status: passed }
    coverage: { status: passed }
    clarity: { status: passed }
    consistency: { status: passed }
  findings:
    - id: F-001
      phase: clarity
      severity: WARNING
      section: "3. Catalogue: Topic `early`"
      section_hash: 0c087facd8b60496
      fragment: "its position uniformly distributed over draws"
      text: "Uniformity of the correct option's position has no tolerance, so the leak test cannot fail or pass deterministically."
      fix: "The plan's leak test asserts each of the three positions holds the answer in 33% ± 5 percentage points of 3 000 draws."
      verdict: open
      verdict_at: null
    - id: F-002
      phase: clarity
      severity: WARNING
      section: "4. Contract, Engine and Profile"
      section_hash: b57cd12e36c62c19
      fragment: "the sticker for the n-th such round is STICKERS[theme][n mod 8]"
      text: "Reward and sticker name the same entity in sections 4 and 5."
      fix: "The plan and code use reward for the API field and sticker for the drawn asset, stated once in the progress schema docstring."
      verdict: open
      verdict_at: null
chain:
  intent: docs/superpowers/intents/2026-09-26-early-numeracy-game-tasks-intent.md
---
# Early Numeracy Game Tasks Design

**Date:** 2026-09-26
**Status:** approved
**Scope:** game-form, picture-first tasks for children aged 4–5 inside the existing mmath practice engine; deployment to the LAN host and the supervised child check are human checkpoints, not authorized by this document.

## 1. Decision and Alternatives

New task kinds live inside the existing session engine as ordinary catalogue skills of a new topic `early`. The public problem carries a scene (`items`) and, where the child answers by card, an unmarked `options` list; the answer stays an integer graded by the server; the session, replay, resume, hint and policy contracts are inherited unchanged. The frontend gains one bounded module `features/game/early/` that renders each kind with the objects of the child's theme and accepts taps.

Rejected: a separate early-numeracy module with its own routes and session type (duplicates the session, replay and resume contract and doubles the surface for answer leaks); client-side games that only report results (violates the hard constraint that the server grades every kind).

Decisions taken with the owner during brainstorming: a new topic `early` rather than spreading the skills over existing topics; the round length becomes a parent choice of 6 or 10 tasks; rewards are derived from finished rounds without a new table; answer cards are three per task.

## 2. Acceptance (from intent)

Desired Outcomes, verbatim from the intent:

- O1 — A child aged 4–5 completes a round without reading and without the keypad: every task is spoken aloud, every task is shown with the objects of the child's theme, and every answer is given by tapping a picture, a card or the objects themselves.
- O2 — A round for a child aged 4–5 contains at least five distinct game forms (for example count, which has more, make the same, quick look, what comes next, who is in the garage), not a single form repeated ten times.
- O3 — After a round the child receives a reward of their theme and can see the collection of rewards earned so far.
- O4 — The parent sees the new early-numeracy skills in the progress view alongside the existing ones: counting, comparing groups, patterns, size and shape.
- O5 — A supervised check with a real four-year-old: the child finishes a round on their own and asks for another one.

Done when (verbatim): the five Desired Outcomes are observable on the LAN deployment — a 4–5-year-old profile plays a spoken, picture-only round with at least five game forms, receives a theme reward and sees the collection, the parent sees the new skills in progress — and the supervised check with the real four-year-old (O5) has been performed and recorded in the task ledger.

Health metrics with the numbers this design fixes (closing intent findings F-001 and F-002): frontend bundle JS+CSS gzip ≤ 160 KB (baseline 96.6 KB JS + 1.7 KB CSS on 2026-09-26); `POST /api/v1/sessions` `duration_ms` p95 ≤ 60 ms over at least 20 session starts on minipc after deployment (baseline p50 14 ms, p95 28 ms, n = 5 from the API request log); all strict GWT scenarios and existing tests green; no answer leak for any kind; children aged 6–10 render byte-for-byte as before; PWA offline behaviour unchanged.

## 3. Catalogue: Topic `early`

Topic `early` ("Малышам" / "Little ones") joins the six existing topics. Nine skills, bands 0 (within 5) and 1 (within 10); existing skill codes, topics and bands are untouched. Every generator is deterministic for `(session, ordinal, skill, band)` and produces the whole `prompt`, including item placement, option values and their shuffle.

| Skill | kind | Public prompt | Correct answer | Input |
|---|---|---|---|---|
| `count_objects` | `count` | `items: [{x, y, icon}]` — the scene; the number is never written | `len(items)` | tap each object (it is marked), then "Done" |
| `make_same` | `match` | `items` of the model set | `len(items)` | tap "+" to add an object to the tray, tap an object to remove it, "Done" |
| `quick_look` | `subitize` | `items` in a dice or domino arrangement (1–5, band 1: 1–6 and two dice), `reveal_ms: 1500`, `options: [3 numbers]` | the count | the scene hides after `reveal_ms`; three cards |
| `what_next` | `pattern` | `sequence: [icon…]` (band 0: AB; band 1: ABB, AAB, ABC), `options: [3 icon indices]` | the next icon index | three picture cards |
| `five_frame` | `frame` | `size: 5` (band 1: `10`), `filled: k`, `k ≠ size/2` | `size − k` | three number cards |
| `order_size` | `order` | `heights: [3, 1, 2]` (3 towers; band 1: 4) | tap order encoded as a number of one-based indices, e.g. `231` | tap the towers from lowest to highest; a "Reset" button clears the taps |
| `share_equal` | `share` | `total`, `friends: 2` (band 1: 2 or 3, `total` divisible) | `total / friends` | three number cards |
| `find_shape` | `pick` | `attribute: "shape"`, `target`, `items: [{shape, size}]` | index of the matching item | tap the item |
| `pick_size` | `pick` | `attribute: "size"`, `target: "largest" \| "smallest"`, `items` | index of the matching item | tap the item |

Kind semantics: `count` and `match` share a prompt shape and differ only in the interaction; `subitize` is graded like `count`, the timer is user experience only and the server never sees it; `order` generators issue at most four towers so the encoded permutation stays within the existing `answer ≤ 100 000` bound; `pick` items carry both `shape` and `size` so one renderer serves both skills.

Hints: `HintView.kind` gains `scene` — the client redraws the same scene with scaffolding (rows of five for `count`/`match`/`subitize`, a bracket over the repeating unit for `pattern`, pair lines for `share`, the frame itself for `frame`, nothing extra for `order`/`pick`). The hint carries no more than the scene already shows, and, as today, exposing it resets the promotion streak.

Answer leak rule, refined: no public field of any kind equals the correct answer, except `prompt.options`, which is the only place the answer may appear — always at least three distinct values, the answer exactly once, its position uniformly distributed over draws. For `count`, `match` and `subitize` the scene is the question; the prompt carries item placements, never the count.

Tier A visual layers on existing skills (kinds unchanged): `compare` at band 0 draws two piles to tap plus a "same" card and stops issuing zero piles; `odd_even` draws pairs with the question "Did everyone get a partner?" and Yes/No cards; `neighbour_one` draws train carriages with one empty; `missing` hides the blanked objects behind a garage or house; `subtraction` animates objects leaving; `addition` fills a basket.

## 4. Contract, Engine and Profile

`PublicProblem.kind` extends to fifteen literals (`result, missing, chain, sequence, compare, parity, operator, count, match, subitize, pattern, frame, order, share, pick`); `operand_a`/`operand_b` are `0` for early kinds; `prompt` stays a JSON object in OpenAPI and becomes a discriminated union by `kind` on the frontend. The contract is regenerated and the contract test updated. `Problem.kind` column widens from 12 to 20 characters in migration 0010.

Picture mode: `start_session` copies `picture_mode = player.age <= 5` and `round_tasks` into `session.settings`; issued problems stay immutable, so both decisions are made at issue time. In picture mode `_issue` adds `prompt.options` (three numbers, deterministic shuffle from the seed) to `result`, `missing` and `sequence` problems at bands 0–1, so the child answers with a card. Outside picture mode prompts are byte-for-byte as before. A profile change applies to the next session, as today.

Round length: `Player.round_tasks ∈ {6, 10}` (migration 0010, server default 10; profile creation defaults to 6 when `age ≤ 5`); `session.settings.round_tasks` replaces the `TOTAL_PROBLEMS` constant in the engine; `SessionSnapshot.total_problems` already exists. The parent edits it in the profile settings.

Topic default: a profile created with `age ≤ 5` and no explicit topics gets `["early", "addition", "subtraction", "counting"]`; the parent adds or removes topics with the existing checkboxes. Profile schemas accept `early`.

Grader, policy and skill state are unchanged: `grade` compares integers; `PolicyState`, legal actions, promotion (five unhinted correct), error streaks and rotation apply to early skills like any other. `classify` returns `None` for early kinds.

Rewards without a table: `GET /players/{id}/progress` gains `rewards: {count, latest}`; a reward is earned for every finished session with `answered_count ≥ total_problems / 2`; the sticker for the n-th such round is `STICKERS[theme][n mod 8]`. The summary screen shows the newly earned sticker; the child home shows the collection shelf.

## 5. Frontend

New module `frontend/src/features/game/early/`: `EarlyTask.tsx` dispatches by `kind` to `CountScene`, `MatchScene`, `QuickLook`, `PatternRow`, `FiveFrame`, `OrderTowers`, `ShareScene`, `PickScene`; `PictureCards.tsx` renders the three options as large cards (numeral plus the same number of dots, or a theme icon); `useSpeech.ts` wraps `speechSynthesis`. `GamePage` renders through `EarlyTask`/`PictureCards` when the snapshot settings carry `picture_mode`, otherwise through the existing `TaskPicture`, `NumberPad` and `ChoicePad` — a vitest snapshot fixes the age-7 rendering.

Input: cards and taps call the existing `submitValue(int)`; `order` accumulates taps and submits on the last one; `count`/`match` submit on "Done"; no drag anywhere. Tier A layers live in `TaskPicture.tsx`; the leaving animation is a 600 ms CSS transition disabled under `prefers-reduced-motion`.

Speech: on each new task in picture mode the prompt phrase `speak.<kind>` is spoken with the first voice matching the current language (`ru-RU`/`en-GB`); a speaker button repeats it; feedback is spoken too; with no matching voice the feature stays silent without errors; on iOS the first utterance follows the child's tap on "Play". No external text-to-speech.

Assets: `frontend/src/assets/themes/<theme>.tsx` holds inline SVG components — per theme four objects, a scene (basket, garage, train, tray), two characters for sharing and eight stickers; shared shapes (circle, square, triangle) and dice/domino dots. All drawn by hand as simple forms under the repository licence, recorded in `frontend/src/assets/ASSETS.md`. `scripts/check_assets.py` gains a gzip measurement of `dist/assets` against the 160 KB budget.

Localisation: `topic.early`, `skill.*` for the nine skills, `speak.*`, `cards.*` and the tier A phrases in both languages.

## 6. Verification

Backend: a catalogue-wide test over the nine skills, both bands and 3 000 draws each (solver equals grader; the leak rule of section 3 holds; every `order` permutation grades; `frame` never issues `k = size/2`; `pattern` options hold exactly one correct icon); `picture_mode` tests (age 4 → options on result/missing at band 0; age 7 → prompts unchanged); `round_tasks` tests (6 → the session finishes after six; inherited into settings); rewards tests (0 finished rounds → 0; three finished → 3 with a deterministic `latest`); migration 0010 upgrade and downgrade.

Frontend: vitest for `EarlyTask` per kind (the scene contains `len(items)` objects; cards never mark the correct one), `PictureCards`, `useSpeech` without voices, and the age-7 `GamePage` snapshot. Playwright: a four-year-old plays a full six-task round by taps only, receives a sticker and starts again with "Once more!"; a seven-year-old sees the previous number pad; a parent toggles the `early` topic and switches 6/10.

Strict GWT scenarios in domain mmath: new `early-round-playable-by-tapping` (O1, O2), `answer-options-never-mark-the-correct-card`, `round-length-follows-profile`, `theme-reward-derived-from-finished-rounds`; `task-shapes-solvable-from-public-prompt` extends to fifteen kinds with its id unchanged. Bindings: `mental_math.game.catalogue.generate`, `mental_math.game.engine.public_problem`, `mental_math.game.engine.start_session`, `mental_math.players.routes.progress` and the test files above.

Post-deployment on minipc: migrations 0010 applied, readiness ok, an age-4 profile plays two rounds through the edge, bundle gzip and `POST /api/v1/sessions` p95 measured against section 2.

## 7. Slices and Order

S2 contract and `early` catalogue with the leak tests → S3 picture mode, `options`, `round_tasks`, migration 0010, topic default → S4 frontend `early/` module, `PictureCards`, tier A layers → S5 speech, SVG assets, rewards → S6 GWT scenarios, README, wiki → S7 deployment to minipc (proposal-first: the owner's "ок" before `up`), post-deployment checks and metric measurement → S8 supervised check with the real child (human only) → rebase onto master after PR #1 and the PR of this branch.

## 8. Risks and Limits

Russian voices may be absent on Android: every task is solvable with sound off, so speech is a layer, not a dependency. `speechSynthesis` on iOS needs a user gesture: the start tap provides it. `order` with four towers has 24 permutations: a wrong tap is undone with "Reset", not by drag. A hint for `subitize` redraws the hidden scene and therefore lowers the difficulty deliberately; it resets the promotion streak like every hint. The rewards derivation counts finished rounds, so deleting sessions would change the collection — sessions are never deleted by the application.
