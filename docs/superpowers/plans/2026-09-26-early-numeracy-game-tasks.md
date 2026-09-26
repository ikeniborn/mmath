---
topic: early-numeracy-game-tasks
review:
  plan_hash: 15b2cd4e7a520b67
  last_run: 2026-09-26
  phases:
    structure: { status: passed }
    coverage: { status: passed }
    dependencies: { status: passed }
    verifiability: { status: passed }
    consistency: { status: passed }
  findings:
    - id: F-001
      phase: dependencies
      severity: WARNING
      section: "Task 7: Browser Journeys, GWT Scenarios and Documentation"
      section_hash: d03efd85f6196476
      fragment: "await page.getByRole('button', { name: 'Дальше' }).click();"
      text: "The feedback button label is assumed; the plan itself tells the implementer to read Feedback.tsx first."
      fix: "Use the Russian text of the game.next key from i18n.tsx (whatever Feedback.tsx renders) in the journey."
      verdict: open
      verdict_at: null
    - id: F-002
      phase: verifiability
      severity: WARNING
      section: "Task 6: Speech, SVG Assets, Stickers and Parent Controls"
      section_hash: 4a02723ecf9978d2
      fragment: "Add to SessionSummary a test that with rewards.count = 3 and theme cars the sticker cars-3 is shown"
      text: "The SessionSummary and PlayerSettings tests are described, not written out."
      fix: "Write both vitest cases when executing Task 6: stubbed fetch returning rewards {count: 3, latest: 'cars-3'} renders .sticker-new; the settings form PATCH body carries round_tasks and topics including early."
      verdict: open
      verdict_at: null
result_check:
  verdict: OK
  plan_hash: 15b2cd4e7a520b67
  base: dev-mental-math-web-platform
  head: 654a934
  last_run: 2026-09-26
chain:
  intent: docs/superpowers/intents/2026-09-26-early-numeracy-game-tasks-intent.md
  spec: docs/superpowers/specs/2026-09-26-early-numeracy-game-tasks-design.md
---
# Early Numeracy Game Tasks Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking. Execution is parent-owned; delegation needs separate authorization.

**Status:** approved

**Goal:** A child aged 4–5 plays a spoken, picture-only round of at least five game forms by tapping, earns a theme sticker, and the parent sees the new skills in progress — without changing what children aged 6–10 see.

**Architecture:** Nine skills of a new topic `early` join the existing catalogue with eight new task kinds; the public problem carries a scene and, for card answers, an unmarked `options` list; the answer stays an integer graded by the server. `picture_mode` and `round_tasks` are decided at session start and stored in the session settings. The frontend gains one module `features/game/early/` that renders each kind with theme SVG objects and answers by tap; speech, stickers and tier A visual layers sit beside it.

**Tech Stack:** Python/FastAPI/Pydantic, SQLAlchemy/Alembic, PostgreSQL 18, pytest; React/TypeScript/Vite, CSS Modules, vitest + Testing Library, Playwright; browser `speechSynthesis`; inline SVG.

**Spec:** [approved design](../specs/2026-09-26-early-numeracy-game-tasks-design.md), body hash `33cbdd0d2824a6e9`.

**Intent:** [approved intent](../intents/2026-09-26-early-numeracy-game-tasks-intent.md), body hash `878235b74d165bf2`.

## Global Constraints

- The correct answer never reaches the client: not in `PublicProblem`, a hint, a picture, a card or a timer payload. `prompt.options` is the only field allowed to contain the answer: at least three distinct values, the answer exactly once, each of the three positions holding the answer in 33 % ± 5 percentage points of 3 000 draws (closes spec finding F-001).
- The server grades every kind from the stored problem (`grade(problem, answer)`); issued problems are immutable; new kinds follow the existing session, replay and resume contract.
- Existing skill codes, topics and bands keep their names; profiles aged 6–10 render byte-for-byte as before (pictures, cards and speech apply only when `session.settings.picture_mode` is true).
- Numbers: within 5 at band 0, within 10 at band 1 for every `early` skill.
- Bundle budget JS+CSS gzip ≤ 160 KB (baseline 98.3 KB); `POST /api/v1/sessions` `duration_ms` p95 ≤ 60 ms over ≥ 20 starts on minipc after deployment (baseline p95 28 ms).
- Naming (closes spec finding F-002): `reward` is the API field and the count; `sticker` is the drawn asset identified by a sticker code `<theme>-<1..8>`.
- Russian and English strings for every new key; strict GWT scenarios in domain mmath for every new observable behaviour; no external CDN, font, script, asset or text-to-speech; no new data about the child.
- Themes stay a free per-profile choice with no gender attribute; the policy legal action set is unchanged.
- Deployment to minipc happens only after the owner's "ок" (proposal-first); the supervised child check (S8) is human-only.

---

## File Structure

| Path | Responsibility | Task |
|---|---|---|
| `backend/mental_math/game/early.py` | Generators and predicates of the nine `early` skills; scene, dice and option helpers | 1 |
| `backend/mental_math/game/catalogue.py` | Registers the `early` skills and topic; compare band 0 without zero piles | 1 |
| `backend/mental_math/game/schemas.py` | `PublicProblem.kind` with 15 literals; `HintView.kind` gains `scene` | 1 |
| `backend/mental_math/game/hints.py`, `student/errors.py` | `scene` hint for early kinds; `classify` returns `None` for them | 1 |
| `backend/mental_math/game/models.py`, `migrations/versions/0010_early_numeracy.py` | `Problem.kind` widened to 20; `players.round_tasks` | 1 |
| `backend/tests/unit/test_early_catalogue.py`, `test_public_view_hides_answers.py` | Solver = grader for every early skill; refined leak rule; option uniformity | 1 |
| `backend/mental_math/game/engine.py` | `picture_mode`, `round_tasks` in session settings; `options` at issue time; round length from settings | 2 |
| `backend/mental_math/players/{models,schemas,routes}.py` | `round_tasks`, topic `early`, age-based defaults, `rewards` in progress | 2, 3 |
| `backend/mental_math/players/rewards.py` | Reward count and sticker code from finished sessions | 3 |
| `backend/tests/conftest.py`, `tests/integration/test_early_sessions.py`, `test_rewards.py` | Solver for early kinds; picture mode, round length, rewards | 2, 3 |
| `frontend/src/api-schema.json`, `api-types.ts` | Regenerated contract | 2 |
| `frontend/src/assets/themes/{index,flowers,dolls,cars,construction,shared}.tsx`, `ASSETS.md` | Inline SVG objects, scenes, characters, stickers, shapes, dice | 4 |
| `frontend/src/features/game/early/{types,EarlyTask,PictureCards,scenes}.tsx` (+ `.module.css`, tests) | Kind dispatcher, scenes, tap inputs, cards | 4 |
| `frontend/src/features/game/GamePage.tsx`, `prompt.ts`, `sessionReducer.ts` | Picture-mode branch; early answer labels | 4 |
| `frontend/src/features/game/TaskPicture.tsx` (+ test) | Tier A layers: piles, pairs, carriages, garage, leaving, basket | 5 |
| `frontend/src/features/game/early/useSpeech.ts` (+ test) | Spoken prompts and feedback | 6 |
| `frontend/src/features/game/SessionSummary.tsx`, `ChildHome.tsx`, `players/PlayerSettings.tsx`, `PlayerPicker.tsx` | Sticker, shelf, `round_tasks`, topic `early`, no client-side topic default | 6 |
| `scripts/check_assets.py` | Gzip budget | 6 |
| `frontend/e2e/early-round.spec.ts`, `helpers.ts`, `README.md`, `docs/README.ru.md`, wiki pages | Browser journeys, docs, GWT scenarios | 7 |
| `deploy/minipc-lan.sh` (unchanged), runbook note | Deployment and post-deployment checks | 8 |

## Delivery Order

| Task | Slice | Observable result | Depends on |
|---|---|---|---|
| 1 Early catalogue | S2 | Nine `early` skills generate leak-free, solvable tasks | — |
| 2 Session settings and contract | S3 | Age-4 profile gets 6-task rounds with `options`; age-7 unchanged | 1 |
| 3 Rewards | S3 | Progress reports reward count and latest sticker code | 2 |
| 4 Early frontend module | S4 | Every early kind renders as a scene and answers by tap or card | 2 |
| 5 Tier A layers | S4 | Compare, parity, neighbour, missing, subtraction, addition draw scenes | 4 |
| 6 Speech, assets, stickers, settings | S5 | Spoken tasks, SVG themes, sticker on summary and shelf, parent controls | 4, 3 |
| 7 Browser journeys, GWT, docs | S6 | Playwright round by taps; scenarios and README current | 5, 6 |
| 8 Deployment and post-deployment checks | S7 | Live on minipc, metrics measured, ledger updated | 7 |

---

### Task 1: Early Catalogue (topic `early`, eight kinds)

**Files:**
- Create: `backend/mental_math/game/early.py`
- Modify: `backend/mental_math/game/catalogue.py` (import, `RAW`, `TOPICS`, `compare` band 0)
- Modify: `backend/mental_math/game/schemas.py` (`PublicProblem.kind`, `HintView.kind`)
- Modify: `backend/mental_math/game/hints.py`, `backend/mental_math/student/errors.py`, `backend/mental_math/game/generator.py` (docstring)
- Modify: `backend/mental_math/game/models.py` (`Problem.kind` String(20))
- Create: `backend/migrations/versions/0010_early_numeracy.py`
- Create: `backend/tests/unit/test_early_catalogue.py`
- Modify: `backend/tests/unit/test_public_view_hides_answers.py`

**Interfaces:**
- Produces: `EARLY_KINDS = frozenset({"count", "match", "subitize", "pattern", "frame", "order", "share", "pick"})` in `early.py`; `answer_options(rng, answer, low, high) -> list[int]` in `early.py` (reused by Task 2); nine skills in `CATALOGUE` with topic `"early"`; `"early"` appended to `TOPICS`.
- Prompt shapes (consumed by Tasks 2, 4): `count`/`match`: `{"items": [{"x": int, "y": int, "icon": int}]}`; `subitize`: `{"items": [...], "reveal_ms": 1500, "options": [int, int, int]}`; `pattern`: `{"sequence": [int...], "options": [int, int, int]}`; `frame`: `{"size": 5|10, "filled": int, "options": [...]}`; `order`: `{"heights": [int...]}`; `share`: `{"total": int, "friends": int, "options": [...]}`; `pick`: `{"attribute": "shape"|"size", "target": str, "items": [{"shape": str, "size": int}]}`.

- [ ] **Step 1: Write the failing catalogue test**

```python
# backend/tests/unit/test_early_catalogue.py
from collections import Counter
from uuid import uuid4

import pytest

from mental_math.game.catalogue import CATALOGUE, TOPICS, generate, skills_for_topics
from mental_math.game.early import EARLY_KINDS

EARLY = ["count_objects", "make_same", "quick_look", "what_next", "five_frame", "order_size", "share_equal", "find_shape", "pick_size"]


def solve(problem) -> int:
    """Independent solver from the public prompt only."""
    kind, prompt = problem.kind, problem.prompt
    if kind in {"count", "match", "subitize"}:
        return len(prompt["items"])
    if kind == "pattern":
        seq = prompt["sequence"]
        period = next(p for p in range(1, len(seq)) if all(seq[i] == seq[i - p] for i in range(p, len(seq))))
        return seq[len(seq) - period]
    if kind == "frame":
        return prompt["size"] - prompt["filled"]
    if kind == "order":
        heights = prompt["heights"]
        return int("".join(str(i + 1) for i in sorted(range(len(heights)), key=lambda i: heights[i])))
    if kind == "share":
        return prompt["total"] // prompt["friends"]
    if kind == "pick":
        items = prompt["items"]
        if prompt["attribute"] == "shape":
            return next(i for i, item in enumerate(items) if item["shape"] == prompt["target"])
        pick = max if prompt["target"] == "largest" else min
        return items.index(pick(items, key=lambda item: item["size"]))
    raise AssertionError(kind)


def test_topic_early_lists_nine_skills_with_bands_zero_and_one():
    assert "early" in TOPICS
    assert sorted(skill.code for skill in skills_for_topics(["early"])) == sorted(EARLY)
    assert all(CATALOGUE[code].bands == (0, 1) for code in EARLY)


@pytest.mark.parametrize("code", EARLY)
def test_solver_equals_grader_and_ranges_follow_the_band(code):
    session = uuid4()
    for band in (0, 1):
        limit = 5 if band == 0 else 10
        for ordinal in range(1, 301):
            p = generate(code, session, ordinal, band)
            assert p.kind in EARLY_KINDS and p.operand_a == 0 and p.operand_b == 0
            assert solve(p) == p.correct_answer, (code, band, p)
            assert CATALOGUE[code].check(p), (code, band, p)
            if p.kind in {"count", "match", "subitize"}:
                assert 1 <= len(p.prompt["items"]) <= limit
                cells = {(item["x"], item["y"]) for item in p.prompt["items"]}
                assert len(cells) == len(p.prompt["items"])  # no two objects share a cell
            if p.kind == "frame":
                assert p.prompt["size"] == limit and p.prompt["filled"] * 2 != p.prompt["size"]
            if p.kind == "share":
                assert p.prompt["friends"] != p.correct_answer and p.prompt["total"] <= limit
            if p.kind == "order":
                assert len(p.prompt["heights"]) == (3 if band == 0 else 4) and len(set(p.prompt["heights"])) == len(p.prompt["heights"])


@pytest.mark.parametrize("code", ["quick_look", "what_next", "five_frame", "share_equal"])
def test_options_hold_the_answer_once_in_a_uniform_position(code):
    positions = Counter()
    for band in (0, 1):
        for ordinal in range(1, 1501):
            p = generate(code, uuid4(), ordinal, band)
            options = p.prompt["options"]
            assert len(options) == 3 == len(set(options)) and options.count(p.correct_answer) == 1
            positions[options.index(p.correct_answer)] += 1
    assert sum(positions.values()) == 3000
    for slot in range(3):
        assert 840 <= positions[slot] <= 1160, positions  # 33 % ± 5 pp


def test_pattern_options_hold_exactly_one_correct_icon():
    for ordinal in range(1, 301):
        p = generate("what_next", uuid4(), ordinal, 1)
        assert sum(1 for option in p.prompt["options"] if option == p.correct_answer) == 1
        assert set(p.prompt["sequence"]) <= set(range(4)) and 5 <= len(p.prompt["sequence"]) <= 6
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `uv run --project backend pytest backend/tests/unit/test_early_catalogue.py -q`
Expected: FAIL with `ModuleNotFoundError: No module named 'mental_math.game.early'`

- [ ] **Step 3: Implement the generators**

```python
# backend/mental_math/game/early.py
"""Early numeracy skills for ages 4-5: scenes of countable objects answered by tapping, never by numerals.

Kinds: count (tap each object), match (build the same number), subitize (a dice or domino scene hidden after a
moment, answered by card), pattern (the next icon of a repeating unit), frame (how many empty cells of a five or
ten frame), order (tap towers from lowest to highest; the answer is the tap order as one-based indices), share
(candies shared equally between friends), pick (tap the item with the named shape or size).
The prompt is the question; the only field ever allowed to contain the answer is `options`, unmarked and shuffled.
"""

import random

from mental_math.game.generator import GeneratedProblem

EARLY_KINDS = frozenset({"count", "match", "subitize", "pattern", "frame", "order", "share", "pick"})
ICONS = 4  # icon indices per theme; the frontend maps an index to a theme object
GRID_W, GRID_H = 5, 4
DICE = {1: [(1, 1)], 2: [(0, 0), (2, 2)], 3: [(0, 0), (1, 1), (2, 2)], 4: [(0, 0), (2, 0), (0, 2), (2, 2)], 5: [(0, 0), (2, 0), (1, 1), (0, 2), (2, 2)], 6: [(0, 0), (2, 0), (0, 1), (2, 1), (0, 2), (2, 2)]}
SHAPES = ("circle", "square", "triangle", "star")
REVEAL_MS = 1500


def _early(operation: str, answer: int, prompt: dict) -> GeneratedProblem:
    return GeneratedProblem(skill="", band=0, operation=operation, operand_a=0, operand_b=0, correct_answer=answer, kind=operation, prompt=prompt)


def _limit(band: int) -> int:
    return 5 if band == 0 else 10


def scene(rng: random.Random, count: int, icon: int | None = None) -> list[dict]:
    """`count` objects on distinct cells of a 5x4 grid."""
    cells = rng.sample(range(GRID_W * GRID_H), count)
    return [{"x": cell % GRID_W, "y": cell // GRID_W, "icon": rng.randrange(2) if icon is None else icon} for cell in cells]


def dice(rng: random.Random, value: int, offset: int = 0) -> list[dict]:
    icon = rng.randrange(2)
    return [{"x": x + offset, "y": y, "icon": icon} for x, y in DICE[value]]


def answer_options(rng: random.Random, answer: int, low: int, high: int) -> list[int]:
    """Three distinct values including the answer once, shuffled so every position is equally likely."""
    pool = [value for value in range(low, high + 1) if value != answer]
    options = [answer, *rng.sample(pool, 2)]
    rng.shuffle(options)
    return options


def count_objects(rng: random.Random, band: int) -> GeneratedProblem:
    n = rng.randint(1, _limit(band))
    return _early("count", n, {"items": scene(rng, n, icon=rng.randrange(2))})


def make_same(rng: random.Random, band: int) -> GeneratedProblem:
    n = rng.randint(1, _limit(band))
    return _early("match", n, {"items": scene(rng, n, icon=rng.randrange(2))})


def quick_look(rng: random.Random, band: int) -> GeneratedProblem:
    if band == 0:
        n = rng.randint(1, 5)
        return _early("subitize", n, {"items": dice(rng, n), "reveal_ms": REVEAL_MS, "options": answer_options(rng, n, 1, 6)})
    a, b = rng.randint(1, 5), rng.randint(1, 5)
    return _early("subitize", a + b, {"items": dice(rng, a) + dice(rng, b, offset=4), "reveal_ms": REVEAL_MS, "options": answer_options(rng, a + b, 1, 10)})


def what_next(rng: random.Random, band: int) -> GeneratedProblem:
    icons = rng.sample(range(ICONS), 3)
    a, b, c = icons
    unit = [a, b] if band == 0 else rng.choice([[a, b, b], [a, a, b], [a, b, c]])
    length = 5 if band == 0 else 6
    sequence = [unit[i % len(unit)] for i in range(length)]
    answer = unit[length % len(unit)]
    others = [icon for icon in range(ICONS) if icon != answer]
    options = [answer, *rng.sample(others, 2)]
    rng.shuffle(options)
    return _early("pattern", answer, {"sequence": sequence, "options": options})


def five_frame(rng: random.Random, band: int) -> GeneratedProblem:
    size = _limit(band)
    filled = rng.choice([k for k in range(1, size) if k * 2 != size])
    answer = size - filled
    return _early("frame", answer, {"size": size, "filled": filled, "options": answer_options(rng, answer, 1, size - 1)})


def order_size(rng: random.Random, band: int) -> GeneratedProblem:
    heights = rng.sample(range(1, 6), 3 if band == 0 else 4)
    order = sorted(range(len(heights)), key=lambda i: heights[i])
    return _early("order", int("".join(str(i + 1) for i in order)), {"heights": heights})


def share_equal(rng: random.Random, band: int) -> GeneratedProblem:
    while True:
        friends = 2 if band == 0 else rng.choice([2, 3])
        each = rng.randint(1, _limit(band) // friends)
        if each != friends:  # the friends count must not spell the answer
            return _early("share", each, {"total": each * friends, "friends": friends, "options": answer_options(rng, each, 1, 5)})


def _pick(rng: random.Random, band: int, attribute: str) -> GeneratedProblem:
    n = 3 if band == 0 else 4
    shapes = SHAPES[:3] if band == 0 else SHAPES
    if attribute == "shape":
        target = rng.choice(shapes)
        others = [shape for shape in shapes if shape != target]
        items = [{"shape": rng.choice(others), "size": rng.randint(1, 3)} for _ in range(n)]
        answer = rng.randrange(n)
        items[answer] = {"shape": target, "size": rng.randint(1, 3)}
        return _early("pick", answer, {"attribute": "shape", "target": target, "items": items})
    sizes = rng.sample(range(1, 6), n)
    shape = rng.choice(shapes)
    target = rng.choice(["largest", "smallest"])
    answer = sizes.index(max(sizes) if target == "largest" else min(sizes))
    return _early("pick", answer, {"attribute": "size", "target": target, "items": [{"shape": shape, "size": size} for size in sizes]})


def find_shape(rng: random.Random, band: int) -> GeneratedProblem:
    return _pick(rng, band, "shape")


def pick_size(rng: random.Random, band: int) -> GeneratedProblem:
    return _pick(rng, band, "size")


def early_ok(p: GeneratedProblem) -> bool:
    limit = _limit(p.band) if p.band in (0, 1) else 10
    prompt = p.prompt or {}
    if p.kind in {"count", "match", "subitize"}:
        return p.correct_answer == len(prompt["items"]) and 1 <= p.correct_answer <= limit
    if p.kind == "pattern":
        return p.correct_answer in prompt["options"] and len(prompt["sequence"]) >= 5
    if p.kind == "frame":
        return prompt["size"] - prompt["filled"] == p.correct_answer and prompt["filled"] * 2 != prompt["size"]
    if p.kind == "order":
        return len(set(prompt["heights"])) == len(prompt["heights"]) and 3 <= len(prompt["heights"]) <= 4
    if p.kind == "share":
        return prompt["total"] == p.correct_answer * prompt["friends"] and prompt["friends"] != p.correct_answer
    if p.kind == "pick":
        return 0 <= p.correct_answer < len(prompt["items"])
    return False
```

Register in `catalogue.py` (the predicates receive `band` through `GeneratedProblem.band`, which `generate` sets before the check runs; `early_ok` therefore reads `p.band`):

```python
# catalogue.py — imports
from mental_math.game import early
# catalogue.py — RAW, after the compare entry
    *[(code, "early", code_kind, (0, 1), getattr(early, code), early.early_ok) for code, code_kind in (("count_objects", "count"), ("make_same", "match"), ("quick_look", "subitize"), ("what_next", "pattern"), ("five_frame", "frame"), ("order_size", "order"), ("share_equal", "share"), ("find_shape", "pick"), ("pick_size", "pick"))],
# catalogue.py — TOPICS
TOPICS = ("addition", "subtraction", "counting", "multiplication", "division", "comparison", "early")
```

Because `generate` runs `skill.sample(rng, band)` and only then copies `band` into the returned problem, `early_ok` must be called on the finished problem: keep the existing `test_every_skill_band_pair_keeps_bounds_and_deterministic_answers` (it calls `entry.check(problem)` on the generated problem, which already carries `band`).

Compare band 0 without zero piles: in `compare()` change `n = rng.randint(0, limit)` to `n = rng.randint(1 if band == 0 else 0, limit)` and likewise `str(rng.randint(0, limit))` to `str(rng.randint(1 if band == 0 else 0, limit))`.

Schemas, hints, errors, model:

```python
# schemas.py
class HintView(BaseModel):
    kind: Literal["counters", "ten_frame", "number_line", "groups", "pairs", "target", "scene"]
    ...
class PublicProblem(BaseModel):
    ...
    kind: Literal["result", "missing", "chain", "sequence", "compare", "parity", "operator", "count", "match", "subitize", "pattern", "frame", "order", "share", "pick"]
# hints.py — first lines of render_hint
    if kind in EARLY_KINDS:  # the client redraws the scene with scaffolding; nothing beyond the scene itself
        return HintView(kind="scene", operation=op, operand_a=0, operand_b=0, scale=10)
# errors.py — after the correctness check
    if getattr(problem, "kind", "result") in EARLY_KINDS:
        return None
# models.py
    kind: Mapped[str] = mapped_column(String(20), default="result")
```

Migration:

```python
# backend/migrations/versions/0010_early_numeracy.py
"""Early numeracy: wider problem kinds and the parent-chosen round length.

Revision ID: 0010_early_numeracy
Revises: 0009_player_age_four
"""

from alembic import op
import sqlalchemy as sa

revision = "0010_early_numeracy"
down_revision = "0009_player_age_four"
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column("problems", "kind", type_=sa.String(20), existing_type=sa.String(12))
    op.add_column("players", sa.Column("round_tasks", sa.Integer, nullable=False, server_default="10"))
    op.create_check_constraint("player_round_tasks_allowed", "players", "round_tasks IN (6, 10)")


def downgrade():
    op.drop_constraint("player_round_tasks_allowed", "players", type_="check")
    op.drop_column("players", "round_tasks")
    op.alter_column("problems", "kind", type_=sa.String(12), existing_type=sa.String(20))
```

- [ ] **Step 4: Refine the leak test**

Append to `backend/tests/unit/test_public_view_hides_answers.py` inside the loop of the existing test, after `hint = render_hint(problem)`:

```python
        if problem.kind in EARLY_KINDS:
            # the scene is the question: no top-level number may spell the answer, only the unmarked options may hold it
            top_level = {value for key, value in (view["prompt"] or {}).items() if isinstance(value, int) and key != "options"}
            assert problem.correct_answer not in top_level, (code, band, view)
            assert hint.kind == "scene" and hint.operand_a == 0 and hint.operand_b == 0
```

with `from mental_math.game.early import EARLY_KINDS` at the top.

- [ ] **Step 5: Run the unit tests and the migration**

```bash
docker compose -f compose.test.yaml up -d --wait postgres-test
uv run --project backend pytest backend/tests/unit -q
uv run --project backend alembic -c backend/alembic.ini upgrade head
uv run --project backend alembic -c backend/alembic.ini downgrade 0009_player_age_four
uv run --project backend alembic -c backend/alembic.ini upgrade head
```

Expected: all unit tests pass (the existing catalogue tests now also cover the nine early skills through `CATALOGUE`); both migration directions exit 0.

- [ ] **Step 6: Commit**

```bash
git add backend/mental_math/game/early.py backend/mental_math/game/catalogue.py backend/mental_math/game/schemas.py backend/mental_math/game/hints.py backend/mental_math/game/models.py backend/mental_math/game/generator.py backend/mental_math/student/errors.py backend/migrations/versions/0010_early_numeracy.py backend/tests/unit/test_early_catalogue.py backend/tests/unit/test_public_view_hides_answers.py
git commit -m "feat(catalogue): add the early numeracy topic with eight picture-first task kinds"
```

### Task 2: Session Settings and Contract (picture mode, options, round length, topic default)

**Files:**
- Modify: `backend/mental_math/game/engine.py` (`TOTAL_PROBLEMS` → settings, `picture_mode`, `options`)
- Modify: `backend/mental_math/players/models.py`, `players/schemas.py`, `players/routes.py`
- Modify: `backend/tests/conftest.py` (`solve` for early kinds)
- Create: `backend/tests/integration/test_early_sessions.py`
- Modify: `backend/tests/integration/test_security_contract.py` (topics default), `frontend/src/api-schema.json`, `frontend/src/api-types.ts` (regenerated)

**Interfaces:**
- Consumes: `answer_options`, `EARLY_KINDS` from Task 1.
- Produces: `session.settings` keys `picture_mode: bool`, `round_tasks: int`; `PlayerView.round_tasks: 6 | 10`; `PlayerInput.topics` optional with an age-based default; `PublicProblem.prompt.options` on `result`/`missing`/`sequence` problems in picture mode; `round_length(session) -> int` in `engine.py`.

- [ ] **Step 1: Write the failing integration tests**

```python
# backend/tests/integration/test_early_sessions.py
import pytest

from tests.conftest import make_family, solve, wrong


async def child(app, family, age: int, **extra) -> str:
    response = await family.post("/players", {"name": f"Age{age}", "age": age, **extra})
    assert response.status_code == 201, response.text
    return response.json()


@pytest.mark.asyncio
async def test_age_four_profile_defaults_to_early_topics_six_tasks_and_picture_mode(app, family):
    player = await child(app, family, 4)
    assert player["topics"] == ["early", "addition", "subtraction", "counting"] and player["round_tasks"] == 6
    started = await family.post("/sessions", {"player_id": player["id"]})
    snapshot = started.json()
    assert snapshot["total_problems"] == 6 and snapshot["settings"]["round_tasks"] == 6 and snapshot["settings"]["picture_mode"] is True


@pytest.mark.asyncio
async def test_age_seven_profile_keeps_ten_tasks_and_prompts_without_options(app, family):
    player = await child(app, family, 7, topics=["addition"])
    assert player["topics"] == ["addition"] and player["round_tasks"] == 10
    snapshot = (await family.post("/sessions", {"player_id": player["id"]})).json()
    assert snapshot["total_problems"] == 10 and snapshot["settings"]["picture_mode"] is False
    assert snapshot["current_problem"]["prompt"] in (None, {}) or "options" not in snapshot["current_problem"]["prompt"]


@pytest.mark.asyncio
async def test_picture_mode_adds_unmarked_options_to_numeric_kinds(app, family):
    player = await child(app, family, 4, topics=["addition"])
    snapshot = (await family.post("/sessions", {"player_id": player["id"]})).json()
    problem = snapshot["current_problem"]
    options = problem["prompt"]["options"]
    answer = solve(problem)
    assert len(options) == 3 == len(set(options)) and options.count(answer) == 1
    assert all(isinstance(value, int) and value >= 0 for value in options)


@pytest.mark.asyncio
async def test_early_round_of_six_is_solvable_and_finishes(app, family, counts):
    player = await child(app, family, 4, topics=["early"])
    snapshot = (await family.post("/sessions", {"player_id": player["id"]})).json()
    kinds = set()
    for index in range(6):
        problem = snapshot["current_problem"]
        kinds.add(problem["kind"])
        result = await family.post(f"/sessions/{snapshot['id']}/attempts", {"submission_id": f"6f4b4b3e-9c3f-4c58-9e5e-1f7d5c1a{index:04d}", "problem_id": problem["id"], "answer": solve(problem), "response_ms": 1200, "expected_version": snapshot["version"]})
        assert result.status_code == 200, result.text
        assert result.json()["correct"] is True
        snapshot = result.json()["session"]
        snapshot = (await family.post(f"/sessions/{snapshot['id']}/advance", {"attempt_id": result.json()["attempt_id"], "expected_version": snapshot["version"]})).json()
    assert snapshot["state"] == "finished" and snapshot["answered_count"] == 6 and snapshot["correct_count"] == 6
    assert len(kinds) >= 2  # rotation switches skill after three correct answers
    assert (await counts(player["id"]))["attempts"] == 6


@pytest.mark.asyncio
async def test_wrong_early_answers_are_graded_wrong(app, family):
    player = await child(app, family, 5, topics=["early"])
    snapshot = (await family.post("/sessions", {"player_id": player["id"]})).json()
    problem = snapshot["current_problem"]
    result = await family.post(f"/sessions/{snapshot['id']}/attempts", {"submission_id": "7f4b4b3e-9c3f-4c58-9e5e-1f7d5c1a0001", "problem_id": problem["id"], "answer": wrong(problem, solve(problem)), "response_ms": 900, "expected_version": snapshot["version"]})
    assert result.status_code == 200 and result.json()["correct"] is False


@pytest.mark.asyncio
async def test_round_tasks_is_validated_and_applies_to_new_sessions(app, family):
    assert (await family.post("/players", {"name": "Bad", "age": 6, "topics": ["addition"], "round_tasks": 7})).status_code == 422
    player = await child(app, family, 8, topics=["addition"], round_tasks=6)
    snapshot = (await family.post("/sessions", {"player_id": player["id"]})).json()
    assert snapshot["total_problems"] == 6
```

Extend `solve` in `backend/tests/conftest.py` before the final `raise AssertionError(kind)`:

```python
    if kind in {"count", "match", "subitize"}:
        return len(prompt["items"])
    if kind == "pattern":
        seq = prompt["sequence"]
        period = next(p for p in range(1, len(seq)) if all(seq[i] == seq[i - p] for i in range(p, len(seq))))
        return seq[len(seq) - period]
    if kind == "frame":
        return prompt["size"] - prompt["filled"]
    if kind == "order":
        heights = prompt["heights"]
        return int("".join(str(i + 1) for i in sorted(range(len(heights)), key=lambda i: heights[i])))
    if kind == "share":
        return prompt["total"] // prompt["friends"]
    if kind == "pick":
        items = prompt["items"]
        if prompt["attribute"] == "shape":
            return next(i for i, item in enumerate(items) if item["shape"] == prompt["target"])
        pick = max if prompt["target"] == "largest" else min
        return items.index(pick(items, key=lambda item: item["size"]))
```

and in `wrong`, before `return answer + 100`:

```python
    if problem["kind"] in {"pattern", "pick", "order"}:
        return answer + 1 if answer < 9 else answer - 1
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `uv run --project backend pytest backend/tests/integration/test_early_sessions.py -q`
Expected: FAIL — `round_tasks` unknown (422 on creation) and `KeyError: 'picture_mode'`.

- [ ] **Step 3: Implement the profile fields and defaults**

```python
# players/models.py — inside __table_args__
        CheckConstraint("round_tasks IN (6, 10)", name="player_round_tasks_allowed"),
# players/models.py — column
    round_tasks: Mapped[int] = mapped_column(Integer, default=10, server_default="10")
```

```python
# players/schemas.py
Topic = Literal["addition", "subtraction", "counting", "multiplication", "division", "comparison", "early"]
EARLY_DEFAULT_TOPICS = ["early", "addition", "subtraction", "counting"]


class PlayerInput(BaseModel):
    name: str = Field(min_length=1, max_length=40)
    age: int = Field(ge=4, le=10)
    avatar: Literal["star", "rocket", "fox", "owl"] = "star"
    topics: list[Topic] | None = None  # None: resolved from the age below
    mode: Literal["automatic", "fixed"] = "automatic"
    difficulty_band: int | None = Field(default=None, ge=0, le=4)
    session_minutes: Literal[5, 10, 15] = 10
    theme: Literal["flowers", "dolls", "cars", "construction"] = "flowers"
    round_tasks: Literal[6, 10] | None = None  # None: 6 for ages 4-5, 10 otherwise

    @field_validator("topics")
    @classmethod
    def unique_topics(cls, value: list[str] | None) -> list[str] | None:
        if value is not None and not value:
            raise ValueError("At least one topic is required")
        return None if value is None else list(dict.fromkeys(value))

    @model_validator(mode="after")
    def resolve_defaults(self):
        if self.difficulty_band is None:
            self.difficulty_band = 0 if self.age <= 6 else 1 if self.age <= 8 else 2
        if self.topics is None:
            self.topics = list(EARLY_DEFAULT_TOPICS) if self.age <= 5 else ["addition"]
        if self.round_tasks is None:
            self.round_tasks = 6 if self.age <= 5 else 10
        return self
```

`PlayerPatch` gains `round_tasks: Literal[6, 10] | None = None` and its `topics` literal uses `Topic`. `PlayerView(PlayerInput)` keeps `id: UUID`; because the view is built from `view(player)` add `"round_tasks": player.round_tasks` to `view()` in `players/routes.py`. The existing `test_security_contract.py` line asserting `topics: []` → 422 still holds (an explicit empty list is refused).

- [ ] **Step 4: Implement session settings, round length and options**

```python
# engine.py — imports
import random
from mental_math.game.early import answer_options
# engine.py — replace the TOTAL_PROBLEMS constant usage
DEFAULT_ROUND = 10  # sessions started before round_tasks existed


def round_length(session: LearningSession) -> int:
    return int(session.settings.get("round_tasks", DEFAULT_ROUND))
```

In `snapshot` use `total_problems=round_length(session)`; in `submit_attempt` replace `session.answered_count < TOTAL_PROBLEMS` with `session.answered_count < round_length(session)`. In `start_session`:

```python
    settings = {"mode": player.mode, "difficulty_band": player.difficulty_band, "topics": list(player.topics), "session_minutes": player.session_minutes, "round_tasks": player.round_tasks, "picture_mode": player.age <= 5}
```

In `_issue`, after `generated = generate(...)`:

```python
    prompt = generated.prompt
    if session.settings.get("picture_mode") and generated.kind in {"result", "missing", "sequence"} and band <= 1:
        # A 4-5-year-old answers by card: three unmarked values, the answer once, shuffled from the same seed family.
        rng = random.Random(f"{session.id}:{ordinal}:{code}:{band}:options")
        answer = generated.correct_answer
        prompt = {**(prompt or {}), "options": answer_options(rng, answer, max(0, answer - 2), answer + 2)}
```

and pass `prompt=prompt` into `Problem(...)`. `SessionSettings` schema gains `round_tasks: int = 10` and `picture_mode: bool = False` so old sessions still validate.

- [ ] **Step 5: Run the integration tests and regenerate the contract**

```bash
uv run --project backend pytest backend/tests/integration/test_early_sessions.py backend/tests/integration/test_task_kinds.py backend/tests/integration/test_session_restart.py backend/tests/integration/test_security_contract.py backend/tests/integration/test_parent_settings.py -q
uv run --project backend python scripts/export_openapi.py
(cd frontend && ./node_modules/.bin/openapi-typescript src/api-schema.json -o src/api-types.ts)
uv run --project backend python scripts/check_contract.py
```

Expected: tests pass; `check_contract.py` prints nothing and exits 0. The `test_task_kinds` full-session test walks `TOPICS` — it now includes `early` and passes through the extended solver.

- [ ] **Step 6: Commit**

```bash
git add backend/mental_math/game/engine.py backend/mental_math/game/schemas.py backend/mental_math/players backend/tests/conftest.py backend/tests/integration/test_early_sessions.py frontend/src/api-schema.json frontend/src/api-types.ts
git commit -m "feat(sessions): decide picture mode, answer options and round length at session start"
```

### Task 3: Rewards Derived from Finished Rounds

**Files:**
- Create: `backend/mental_math/players/rewards.py`
- Modify: `backend/mental_math/players/schemas.py` (`RewardsView`, `ProgressView.rewards`), `players/routes.py` (`progress`)
- Create: `backend/tests/integration/test_rewards.py`
- Modify: `frontend/src/api-schema.json`, `frontend/src/api-types.ts` (regenerated)

**Interfaces:**
- Produces: `rewards_for(sessions: list[LearningSession], theme: str) -> dict` returning `{"count": int, "latest": str | None}`; `sticker_code(theme: str, ordinal: int) -> str` = `f"{theme}-{(ordinal - 1) % STICKERS_PER_THEME + 1}"`, `STICKERS_PER_THEME = 8`; `ProgressView.rewards: RewardsView`.

- [ ] **Step 1: Write the failing test**

```python
# backend/tests/integration/test_rewards.py
import pytest

from mental_math.players.rewards import STICKERS_PER_THEME, sticker_code
from tests.conftest import solve


async def play_round(family, player_id: str, answers: int) -> dict:
    snapshot = (await family.post("/sessions", {"player_id": player_id})).json()
    for index in range(answers):
        problem = snapshot["current_problem"]
        result = (await family.post(f"/sessions/{snapshot['id']}/attempts", {"submission_id": f"8f4b4b3e-9c3f-4c58-9e5e-{index:04d}{answers:04d}0000", "problem_id": problem["id"], "answer": solve(problem), "response_ms": 800, "expected_version": snapshot["version"]})).json()
        snapshot = (await family.post(f"/sessions/{snapshot['id']}/advance", {"attempt_id": result["attempt_id"], "expected_version": result["session"]["version"]})).json()
    if snapshot["state"] != "finished":
        snapshot = (await family.post(f"/sessions/{snapshot['id']}/finish")).json()
    return snapshot


@pytest.mark.asyncio
async def test_rewards_count_finished_rounds_with_at_least_half_answered(family):
    player = (await family.post("/players", {"name": "Four", "age": 4, "topics": ["early"], "theme": "cars"})).json()
    progress = (await family.get(f"/players/{player['id']}/progress")).json()
    assert progress["rewards"] == {"count": 0, "latest": None}
    await play_round(family, player["id"], 6)  # full round
    await play_round(family, player["id"], 2)  # abandoned early: no reward
    await play_round(family, player["id"], 3)  # exactly half: reward
    progress = (await family.get(f"/players/{player['id']}/progress")).json()
    assert progress["rewards"] == {"count": 2, "latest": "cars-2"}


def test_sticker_codes_cycle_per_theme():
    assert sticker_code("flowers", 1) == "flowers-1"
    assert sticker_code("flowers", STICKERS_PER_THEME) == f"flowers-{STICKERS_PER_THEME}"
    assert sticker_code("flowers", STICKERS_PER_THEME + 1) == "flowers-1"
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `uv run --project backend pytest backend/tests/integration/test_rewards.py -q`
Expected: FAIL with `ModuleNotFoundError: No module named 'mental_math.players.rewards'`

- [ ] **Step 3: Implement rewards**

```python
# backend/mental_math/players/rewards.py
"""Rewards are derived, never stored: one reward per finished round with at least half of its tasks answered.

`reward` is the API notion (a count and the latest sticker code); a `sticker` is the drawn asset the frontend maps
from the code `<theme>-<1..8>`. Sessions are never deleted by the application, so the derivation is stable.
"""

from mental_math.game.models import LearningSession

STICKERS_PER_THEME = 8
DEFAULT_ROUND = 10


def sticker_code(theme: str, ordinal: int) -> str:
    return f"{theme}-{(ordinal - 1) % STICKERS_PER_THEME + 1}"


def earns_reward(session: LearningSession) -> bool:
    total = int(session.settings.get("round_tasks", DEFAULT_ROUND))
    return session.state == "finished" and session.answered_count * 2 >= total


def rewards_for(sessions: list[LearningSession], theme: str) -> dict:
    count = sum(1 for session in sessions if earns_reward(session))
    return {"count": count, "latest": sticker_code(theme, count) if count else None}
```

```python
# players/schemas.py
class RewardsView(BaseModel):
    count: int
    latest: str | None


class ProgressView(BaseModel):
    skills: list[SkillProgress]
    sessions: list[SessionHistory]
    total_sessions: int
    rewards: RewardsView
```

In `players/routes.py` `progress`: load every session of the child for the derivation (the paginated list stays for history) and add the field:

```python
    all_sessions = (await db.scalars(select(LearningSession).where(LearningSession.player_id == player.id))).all()
    ...
        "rewards": rewards_for(list(all_sessions), player.theme),
```

with `from mental_math.players.rewards import rewards_for`.

- [ ] **Step 4: Run the tests and regenerate the contract**

```bash
uv run --project backend pytest backend/tests/integration/test_rewards.py backend/tests/integration/test_difficulty_modes.py -q
uv run --project backend python scripts/export_openapi.py
(cd frontend && ./node_modules/.bin/openapi-typescript src/api-schema.json -o src/api-types.ts)
uv run --project backend python scripts/check_contract.py
```

Expected: pass; contract check exits 0.

- [ ] **Step 5: Commit**

```bash
git add backend/mental_math/players/rewards.py backend/mental_math/players/schemas.py backend/mental_math/players/routes.py backend/tests/integration/test_rewards.py frontend/src/api-schema.json frontend/src/api-types.ts
git commit -m "feat(progress): derive rewards and sticker codes from finished rounds"
```

### Task 4: Early Frontend Module (scenes, taps, cards)

**Files:**
- Create: `frontend/src/assets/themes/index.tsx` (icon and shape components; the full SVG set arrives in Task 6, this task ships minimal placeholder shapes that Task 6 replaces in place)
- Create: `frontend/src/features/game/early/types.ts`, `EarlyTask.tsx`, `PictureCards.tsx`, `scenes.tsx`, `Early.module.css`, `EarlyTask.test.tsx`, `PictureCards.test.tsx`
- Modify: `frontend/src/features/game/GamePage.tsx`, `prompt.ts`, `sessionReducer.ts` (no change needed unless `entry` typing breaks), `frontend/src/i18n.tsx`

**Interfaces:**
- Consumes: `PublicProblem` with the Task 1 prompt shapes; `SessionSnapshot.settings.picture_mode`.
- Produces: `<EarlyTask problem theme onAnswer={(value: number) => void} disabled />` — renders a scene and its tap input for every early kind and, for numeric kinds with `options`, the cards; `<PictureCards options theme kind onChoose disabled />`; `isEarly(problem): boolean`, `optionsOf(problem): number[] | null` in `types.ts`; `ThemeIcon({theme, icon, className})`, `Shape({shape, size})` in `assets/themes/index.tsx`.

- [ ] **Step 1: Write the failing component tests**

```tsx
// frontend/src/features/game/early/EarlyTask.test.tsx
import { cleanup, fireEvent, render, screen } from '@testing-library/react';
import { afterEach, expect, test, vi } from 'vitest';
import type { PublicProblem } from '../../../api';
import EarlyTask from './EarlyTask';

afterEach(cleanup);
const base = { id: 'p', ordinal: 1, band: 0, operand_a: 0, operand_b: 0 };
const items = [{ x: 0, y: 0, icon: 0 }, { x: 1, y: 0, icon: 0 }, { x: 2, y: 1, icon: 0 }];

test('count: tapping each object once and pressing done submits the count', () => {
  const onAnswer = vi.fn();
  render(<EarlyTask problem={{ ...base, skill: 'count_objects', operation: 'count', kind: 'count', prompt: { items } } as PublicProblem} theme="cars" onAnswer={onAnswer} disabled={false} />);
  const objects = screen.getAllByRole('button', { name: /предмет/i });
  expect(objects).toHaveLength(3);
  fireEvent.click(objects[0]); fireEvent.click(objects[0]); fireEvent.click(objects[2]);  // a second tap on the same object does not count twice
  expect(screen.getByText('2')).toBeTruthy();
  fireEvent.click(screen.getByRole('button', { name: 'Готово' }));
  expect(onAnswer).toHaveBeenCalledWith(2);
});

test('subitize: the scene hides after reveal_ms and a card submits its value; cards never mark the answer', () => {
  vi.useFakeTimers();
  const onAnswer = vi.fn();
  const { container } = render(<EarlyTask problem={{ ...base, skill: 'quick_look', operation: 'subitize', kind: 'subitize', prompt: { items, reveal_ms: 1500, options: [4, 3, 5] } } as PublicProblem} theme="flowers" onAnswer={onAnswer} disabled={false} />);
  expect(container.querySelectorAll('[data-object]')).toHaveLength(3);
  vi.advanceTimersByTime(1500);
  expect(container.querySelector('[data-hidden="true"]')).toBeTruthy();
  const cards = screen.getAllByRole('button', { name: /карточка/i });
  expect(cards.map(card => card.className)).toEqual([cards[0].className, cards[0].className, cards[0].className]);
  fireEvent.click(cards[1]);
  expect(onAnswer).toHaveBeenCalledWith(3);
  vi.useRealTimers();
});

test('order: tapping towers submits the tap order as one-based indices; reset clears', () => {
  const onAnswer = vi.fn();
  render(<EarlyTask problem={{ ...base, skill: 'order_size', operation: 'order', kind: 'order', prompt: { heights: [3, 1, 2] } } as PublicProblem} theme="construction" onAnswer={onAnswer} disabled={false} />);
  const towers = screen.getAllByRole('button', { name: /башня/i });
  fireEvent.click(towers[1]); fireEvent.click(screen.getByRole('button', { name: 'Сначала' })); fireEvent.click(towers[1]); fireEvent.click(towers[2]); fireEvent.click(towers[0]);
  expect(onAnswer).toHaveBeenCalledTimes(1);
  expect(onAnswer).toHaveBeenCalledWith(231);
});

test('pick and pattern submit indices; frame and share offer cards', () => {
  const onAnswer = vi.fn();
  const pick = render(<EarlyTask problem={{ ...base, skill: 'find_shape', operation: 'pick', kind: 'pick', prompt: { attribute: 'shape', target: 'circle', items: [{ shape: 'square', size: 2 }, { shape: 'circle', size: 1 }, { shape: 'triangle', size: 3 }] } } as PublicProblem} theme="dolls" onAnswer={onAnswer} disabled={false} />);
  fireEvent.click(pick.getAllByRole('button', { name: /фигура/i })[1]);
  expect(onAnswer).toHaveBeenLastCalledWith(1);
  const pattern = render(<EarlyTask problem={{ ...base, skill: 'what_next', operation: 'pattern', kind: 'pattern', prompt: { sequence: [0, 1, 0, 1, 0], options: [2, 1, 0] } } as PublicProblem} theme="dolls" onAnswer={onAnswer} disabled={false} />);
  fireEvent.click(pattern.getAllByRole('button', { name: /карточка/i })[1]);
  expect(onAnswer).toHaveBeenLastCalledWith(1);
  const frame = render(<EarlyTask problem={{ ...base, skill: 'five_frame', operation: 'frame', kind: 'frame', prompt: { size: 5, filled: 2, options: [3, 1, 4] } } as PublicProblem} theme="dolls" onAnswer={onAnswer} disabled={false} />);
  expect(frame.container.querySelectorAll('[data-cell="filled"]')).toHaveLength(2);
  expect(frame.container.querySelectorAll('[data-cell="empty"]')).toHaveLength(3);
});
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `(cd frontend && npx vitest run src/features/game/early)`
Expected: FAIL — `Cannot find module './EarlyTask'`.

- [ ] **Step 3: Implement types, scenes, cards and the dispatcher**

```ts
// frontend/src/features/game/early/types.ts
import type { PublicProblem } from '../../../api';

export const EARLY_KINDS = new Set(['count', 'match', 'subitize', 'pattern', 'frame', 'order', 'share', 'pick']);
export type Item = { x: number; y: number; icon: number };
export type PickItem = { shape: 'circle' | 'square' | 'triangle' | 'star'; size: number };

const record = (problem: PublicProblem) => (problem.prompt ?? {}) as Record<string, unknown>;
export const isEarly = (problem: PublicProblem) => EARLY_KINDS.has(problem.kind);
export const itemsOf = (problem: PublicProblem) => (record(problem).items as Item[] | undefined) ?? [];
export const pickItemsOf = (problem: PublicProblem) => (record(problem).items as PickItem[] | undefined) ?? [];
export const optionsOf = (problem: PublicProblem): number[] | null => (record(problem).options as number[] | undefined) ?? null;
export const numberOf = (problem: PublicProblem, key: string, fallback = 0) => Number(record(problem)[key] ?? fallback);
export const listOf = (problem: PublicProblem, key: string) => (record(problem)[key] as number[] | undefined) ?? [];
export const stringOf = (problem: PublicProblem, key: string) => String(record(problem)[key] ?? '');
```

```tsx
// frontend/src/assets/themes/index.tsx — minimal set for Task 4; Task 6 replaces the bodies with the drawn SVGs
import type { Theme } from '../../api';

const FALLBACK: Record<Theme, string[]> = { flowers: ['🌸', '🌼', '🌷', '🌻'], dolls: ['🪆', '🎀', '🧸', '🎈'], cars: ['🚗', '🚙', '🚌', '🚲'], construction: ['🚜', '🚧', '🏗️', '🧱'] };

export function ThemeIcon({ theme, icon, className = '' }: { theme: Theme; icon: number; className?: string }) {
  return <span className={className} aria-hidden="true">{FALLBACK[theme][icon % 4]}</span>;
}

export function Shape({ shape, size }: { shape: string; size: number }) {
  const px = 24 + size * 12;
  const fill = { circle: '#dd7a14', square: '#126d67', triangle: '#a52b20', star: '#c7b46a' }[shape] ?? '#697b83';
  const body = shape === 'circle' ? <circle cx="50" cy="50" r="45" fill={fill} /> : shape === 'square' ? <rect x="8" y="8" width="84" height="84" rx="8" fill={fill} /> : shape === 'triangle' ? <polygon points="50,6 94,90 6,90" fill={fill} /> : <polygon points="50,5 61,38 96,38 68,58 79,92 50,72 21,92 32,58 4,38 39,38" fill={fill} />;
  return <svg viewBox="0 0 100 100" width={px} height={px} aria-hidden="true">{body}</svg>;
}
```

```tsx
// frontend/src/features/game/early/PictureCards.tsx
import type { Theme } from '../../../api';
import { ThemeIcon } from '../../../assets/themes';
import { useT } from '../../../i18n';
import styles from './Early.module.css';

type Props = { options: number[]; theme: Theme; kind: 'number' | 'icon'; disabled: boolean; onChoose: (value: number) => void };

/** Three equal cards; a number card shows the numeral and as many dots, an icon card shows the theme object. Nothing marks the correct one. */
export default function PictureCards({ options, theme, kind, disabled, onChoose }: Props) {
  const { t } = useT();
  return <div className={styles.cards} role="group" aria-label={t('early.cards')}>
    {options.map((value, index) => <button type="button" key={`${value}-${index}`} className={styles.card} disabled={disabled} aria-label={t('early.card', { n: index + 1 })} onClick={() => onChoose(value)}>
      {kind === 'icon' ? <ThemeIcon theme={theme} icon={value} className={styles.cardIcon} /> : <><span className={styles.cardNumber}>{value}</span><span className={styles.dots} aria-hidden="true">{Array.from({ length: value }, (_, dot) => <i key={dot} />)}</span></>}
    </button>)}
  </div>;
}
```

```tsx
// frontend/src/features/game/early/scenes.tsx
import { useEffect, useState } from 'react';
import type { PublicProblem, Theme } from '../../../api';
import { Shape, ThemeIcon } from '../../../assets/themes';
import { useT } from '../../../i18n';
import styles from './Early.module.css';
import PictureCards from './PictureCards';
import { itemsOf, listOf, numberOf, optionsOf, pickItemsOf, stringOf, type Item } from './types';

type SceneProps = { problem: PublicProblem; theme: Theme; disabled: boolean; onAnswer: (value: number) => void };

function Grid({ items, theme, marked, onTap, hidden = false, label }: { items: Item[]; theme: Theme; marked?: Set<number>; onTap?: (index: number) => void; hidden?: boolean; label: string }) {
  return <div className={styles.grid} data-hidden={hidden ? 'true' : undefined}>
    {items.map((item, index) => {
      const style = { gridColumn: item.x + 1, gridRow: item.y + 1 };
      const content = <ThemeIcon theme={theme} icon={item.icon} className={`${styles.object} ${marked?.has(index) ? styles.marked : ''}`} />;
      return onTap ? <button type="button" key={index} style={style} data-object className={styles.objectButton} aria-label={`${label} ${index + 1}`} aria-pressed={marked?.has(index) ?? false} onClick={() => onTap(index)}>{content}</button> : <span key={index} style={style} data-object className={styles.objectButton}>{hidden ? null : content}</span>;
    })}
  </div>;
}

export function CountScene({ problem, theme, disabled, onAnswer }: SceneProps) {
  const { t } = useT();
  const items = itemsOf(problem);
  const [marked, setMarked] = useState<Set<number>>(new Set());
  useEffect(() => setMarked(new Set()), [problem.id]);
  const toggle = (index: number) => setMarked(current => { const next = new Set(current); next.has(index) ? next.delete(index) : next.add(index); return next; });
  return <>
    <Grid items={items} theme={theme} marked={marked} onTap={disabled ? undefined : toggle} label={t('early.object')} />
    <p className={styles.counter} aria-live="polite">{marked.size}</p>
    <button type="button" className={styles.done} disabled={disabled || marked.size === 0} onClick={() => onAnswer(marked.size)}>{t('early.done')}</button>
  </>;
}

export function MatchScene({ problem, theme, disabled, onAnswer }: SceneProps) {
  const { t } = useT();
  const items = itemsOf(problem);
  const [tray, setTray] = useState(0);
  useEffect(() => setTray(0), [problem.id]);
  const trayItems: Item[] = Array.from({ length: tray }, (_, index) => ({ x: index % 5, y: Math.floor(index / 5), icon: 1 }));
  return <>
    <Grid items={items} theme={theme} label={t('early.object')} />
    <div className={styles.tray}>
      <Grid items={trayItems} theme={theme} onTap={disabled ? undefined : () => setTray(count => Math.max(0, count - 1))} label={t('early.trayObject')} />
      <button type="button" className={styles.plus} disabled={disabled || tray >= 10} aria-label={t('early.add')} onClick={() => setTray(count => count + 1)}>+</button>
    </div>
    <button type="button" className={styles.done} disabled={disabled || tray === 0} onClick={() => onAnswer(tray)}>{t('early.done')}</button>
  </>;
}

export function QuickLook({ problem, theme, disabled, onAnswer }: SceneProps) {
  const { t } = useT();
  const [hidden, setHidden] = useState(false);
  useEffect(() => {
    setHidden(false);
    const timer = setTimeout(() => setHidden(true), numberOf(problem, 'reveal_ms', 1500));
    return () => clearTimeout(timer);
  }, [problem.id]);
  return <>
    <Grid items={itemsOf(problem)} theme={theme} hidden={hidden} label={t('early.object')} />
    <PictureCards options={optionsOf(problem) ?? []} theme={theme} kind="number" disabled={disabled} onChoose={onAnswer} />
  </>;
}

export function PatternRow({ problem, theme, disabled, onAnswer }: SceneProps) {
  return <>
    <div className={styles.row}>{listOf(problem, 'sequence').map((icon, index) => <ThemeIcon key={index} theme={theme} icon={icon} className={styles.object} />)}<span className={styles.slot}>?</span></div>
    <PictureCards options={optionsOf(problem) ?? []} theme={theme} kind="icon" disabled={disabled} onChoose={onAnswer} />
  </>;
}

export function FiveFrame({ problem, theme, disabled, onAnswer }: SceneProps) {
  const size = numberOf(problem, 'size', 5), filled = numberOf(problem, 'filled', 0);
  return <>
    <div className={styles.frame} style={{ gridTemplateColumns: `repeat(5, 1fr)` }}>{Array.from({ length: size }, (_, index) => <span key={index} className={styles.cell} data-cell={index < filled ? 'filled' : 'empty'}>{index < filled ? <ThemeIcon theme={theme} icon={0} className={styles.object} /> : null}</span>)}</div>
    <PictureCards options={optionsOf(problem) ?? []} theme={theme} kind="number" disabled={disabled} onChoose={onAnswer} />
  </>;
}

export function OrderTowers({ problem, theme, disabled, onAnswer }: SceneProps) {
  const { t } = useT();
  const heights = listOf(problem, 'heights');
  const [taps, setTaps] = useState<number[]>([]);
  useEffect(() => setTaps([]), [problem.id]);
  const tap = (index: number) => {
    if (taps.includes(index)) return;
    const next = [...taps, index];
    setTaps(next);
    if (next.length === heights.length) onAnswer(Number(next.map(i => i + 1).join('')));
  };
  return <>
    <div className={styles.towers}>{heights.map((height, index) => <button type="button" key={index} className={styles.tower} disabled={disabled || taps.includes(index)} aria-label={`${t('early.tower')} ${index + 1}`} onClick={() => tap(index)}>
      {Array.from({ length: height }, (_, block) => <ThemeIcon key={block} theme={theme} icon={0} className={styles.block} />)}
      {taps.includes(index) && <span className={styles.badge}>{taps.indexOf(index) + 1}</span>}
    </button>)}</div>
    <button type="button" className="secondary" disabled={disabled || taps.length === 0} onClick={() => setTaps([])}>{t('early.reset')}</button>
  </>;
}

export function ShareScene({ problem, theme, disabled, onAnswer }: SceneProps) {
  const total = numberOf(problem, 'total'), friends = numberOf(problem, 'friends');
  return <>
    <div className={styles.row}>{Array.from({ length: total }, (_, index) => <ThemeIcon key={index} theme={theme} icon={1} className={styles.object} />)}</div>
    <div className={styles.row}>{Array.from({ length: friends }, (_, index) => <ThemeIcon key={index} theme={theme} icon={2} className={styles.friend} />)}</div>
    <PictureCards options={optionsOf(problem) ?? []} theme={theme} kind="number" disabled={disabled} onChoose={onAnswer} />
  </>;
}

export function PickScene({ problem, disabled, onAnswer }: SceneProps) {
  const { t } = useT();
  return <div className={styles.row}>{pickItemsOf(problem).map((item, index) => <button type="button" key={index} className={styles.pick} disabled={disabled} aria-label={`${t('early.shape')} ${index + 1}`} onClick={() => onAnswer(index)}><Shape shape={item.shape} size={item.size} /></button>)}</div>;
}

export { stringOf };
```

```tsx
// frontend/src/features/game/early/EarlyTask.tsx
import type { PublicProblem, Theme } from '../../../api';
import PictureCards from './PictureCards';
import { CountScene, FiveFrame, MatchScene, OrderTowers, PatternRow, PickScene, QuickLook, ShareScene } from './scenes';
import { isEarly, optionsOf } from './types';

type Props = { problem: PublicProblem; theme: Theme; disabled: boolean; onAnswer: (value: number) => void };

/** Picture-first task for a 4-5-year-old: a scene per early kind, or number cards for a numeric task issued with options. */
export default function EarlyTask(props: Props) {
  const { problem } = props;
  if (!isEarly(problem)) {
    const options = optionsOf(problem);
    return options ? <PictureCards options={options} theme={props.theme} kind="number" disabled={props.disabled} onChoose={props.onAnswer} /> : null;
  }
  switch (problem.kind) {
    case 'count': return <CountScene {...props} />;
    case 'match': return <MatchScene {...props} />;
    case 'subitize': return <QuickLook {...props} />;
    case 'pattern': return <PatternRow {...props} />;
    case 'frame': return <FiveFrame {...props} />;
    case 'order': return <OrderTowers {...props} />;
    case 'share': return <ShareScene {...props} />;
    default: return <PickScene {...props} />;
  }
}
```

`Early.module.css` (touch targets ≥ 56 px, no motion beyond opacity):

```css
.grid { display: grid; grid-template-columns: repeat(5, 56px); grid-auto-rows: 56px; gap: 6px; justify-content: center; }
.grid[data-hidden="true"] .objectButton { background: #e8e2cf; }
.objectButton { display: grid; place-items: center; min-width: 56px; min-height: 56px; border: 2px solid transparent; border-radius: 14px; background: #fff; }
.object { font-size: 2rem; line-height: 1; }
.marked { filter: drop-shadow(0 0 0 #126d67); outline: 3px solid #126d67; border-radius: 12px; }
.counter { font-size: 3rem; font-weight: 700; text-align: center; margin: 8px 0; }
.done, .plus { min-height: 64px; min-width: 64px; font-size: 1.5rem; border-radius: 16px; }
.tray { display: flex; gap: 12px; align-items: center; justify-content: center; }
.cards { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; }
.card { min-height: 112px; border: 3px solid #697b83; border-radius: 18px; background: #fff; display: grid; place-items: center; }
.cardNumber { font-size: 2.5rem; font-weight: 700; }
.cardIcon { font-size: 2.5rem; }
.dots { display: flex; flex-wrap: wrap; gap: 4px; justify-content: center; max-width: 80px; }
.dots i { width: 10px; height: 10px; border-radius: 50%; background: #126d67; }
.row { display: flex; flex-wrap: wrap; gap: 10px; justify-content: center; align-items: flex-end; }
.slot { font-size: 2rem; font-weight: 700; color: #dd7a14; }
.frame { display: grid; gap: 6px; max-width: 320px; margin: 0 auto; }
.cell { display: grid; place-items: center; height: 56px; border: 2px solid #697b83; border-radius: 8px; background: #fff; }
.towers { display: flex; gap: 16px; justify-content: center; align-items: flex-end; }
.tower { display: flex; flex-direction: column-reverse; gap: 2px; min-width: 64px; padding: 8px; border-radius: 12px; border: 2px solid #697b83; background: #fff; position: relative; }
.block { font-size: 1.6rem; }
.badge { position: absolute; top: -12px; right: -12px; background: #dd7a14; color: #fff; border-radius: 50%; width: 28px; height: 28px; display: grid; place-items: center; font-weight: 700; }
.friend { font-size: 2.5rem; }
.pick { min-width: 96px; min-height: 96px; border-radius: 18px; border: 2px solid #697b83; background: #fff; display: grid; place-items: center; }
```

i18n keys (ru / en): `early.cards` «Карточки с ответами» / "Answer cards"; `early.card` «Карточка {n}» / "Card {n}"; `early.object` «Предмет» / "Object"; `early.trayObject` «Предмет на подносе» / "Tray object"; `early.add` «Добавить» / "Add"; `early.done` «Готово» / "Done"; `early.tower` «Башня» / "Tower"; `early.reset` «Сначала» / "Start over"; `early.shape` «Фигура» / "Shape"; skill names `skill.count_objects` «Сосчитай» / "Count"; `skill.make_same` «Столько же» / "Make the same"; `skill.quick_look` «Быстрый взгляд» / "Quick look"; `skill.what_next` «Что дальше?» / "What comes next?"; `skill.five_frame` «До пяти» / "Up to five"; `skill.order_size` «Лесенка» / "Staircase"; `skill.share_equal` «Поровну» / "Share equally"; `skill.find_shape` «Найди фигуру» / "Find the shape"; `skill.pick_size` «Самый большой» / "Largest or smallest"; `topic.early` «Малышам» / "Little ones"; prompt texts `prompt.count` «Сколько здесь предметов?» / "How many are there?"; `prompt.match` «Положи столько же» / "Put the same number"; `prompt.subitize` «Запомни, сколько было» / "Remember how many"; `prompt.pattern` «Что дальше?» / "What comes next?"; `prompt.frame` «Сколько пустых окошек?» / "How many empty windows?"; `prompt.order` «Нажимай от низкой к высокой» / "Tap from lowest to highest"; `prompt.share` «Сколько получит каждый?» / "How many does each one get?"; `prompt.pick.shape.circle` «Найди круг» / "Find the circle", `.square` «Найди квадрат» / "Find the square", `.triangle` «Найди треугольник» / "Find the triangle", `.star` «Найди звезду» / "Find the star"; `prompt.pick.size.largest` «Найди самый большой» / "Find the largest", `.smallest` «Найди самый маленький» / "Find the smallest".

`prompt.ts`: `promptParts` returns `[t('prompt.<kind>')]` for early kinds (for `pick`: `t(`prompt.pick.${attribute}.${target}`)`); `isChoice` unchanged; `answerLabel` for `pattern`/`pick`/`order` returns `String(value)`.

`GamePage.tsx`: read `const picture = Boolean((snapshot.settings as { picture_mode?: boolean }).picture_mode);` and when `picture && problem` render `<EarlyTask problem={problem} theme={player.theme} disabled={status !== 'ready'} onAnswer={submitValue} />` in place of the `ChoicePad`/`NumberPad` branch **only when** `isEarly(problem) || optionsOf(problem)`; otherwise fall through to the existing branch. Keyboard digits are ignored in picture mode. The `.expression` paragraph keeps rendering (accessible text), so `readAnswer` in e2e helpers still works for numeric kinds.

- [ ] **Step 4: Run typecheck and vitest**

Run: `(cd frontend && npm run typecheck && npx vitest run)`
Expected: PASS; the existing `TaskPicture`, `Hint` and `GamePage`-related tests unchanged.

- [ ] **Step 5: Commit**

```bash
git add frontend/src/assets/themes/index.tsx frontend/src/features/game/early frontend/src/features/game/GamePage.tsx frontend/src/features/game/prompt.ts frontend/src/i18n.tsx
git commit -m "feat(ui): render early numeracy tasks as tappable scenes and cards"
```

### Task 5: Tier A Visual Layers on Existing Skills

**Files:**
- Modify: `frontend/src/features/game/TaskPicture.tsx`, `TaskPicture.test.tsx`, `prompt.ts` (parity yes/no labels in picture mode), `GamePage.tsx` (pass `picture` flag), `Hint.module.css` or new `TaskPicture.module.css`, `frontend/src/i18n.tsx`

**Interfaces:**
- Consumes: `ThemeIcon` from Task 4.
- Produces: `pictureKind(problem, picture: boolean): 'add' | 'sub' | 'missing' | 'compare' | 'parity' | 'neighbour' | null`; `<TaskPicture problem theme picture onAnswer disabled />` — for `compare` the piles are the input (tap a pile or the "same" card), for `parity` Yes/No cards.

- [ ] **Step 1: Write the failing tests**

Replace `TaskPicture.test.tsx` cases with picture-mode flags and add:

```tsx
test('compare draws two tappable piles and a same card; tapping the larger pile submits 1 or -1', () => {
  const onAnswer = vi.fn();
  render(<TaskPicture problem={{ ...add, skill: 'compare', operation: 'compare', kind: 'compare', operand_a: 3, operand_b: 5, prompt: { left: '3', right: '5' } }} theme="cars" picture onAnswer={onAnswer} disabled={false} />);
  const piles = screen.getAllByRole('button', { name: /кучка/i });
  expect(piles[0].querySelectorAll('span').length).toBe(3);
  fireEvent.click(piles[1]);
  expect(onAnswer).toHaveBeenCalledWith(-1);  // left < right
  fireEvent.click(screen.getByRole('button', { name: 'Одинаково' }));
  expect(onAnswer).toHaveBeenLastCalledWith(0);
});

test('parity draws pairs with the odd one out and Yes/No cards', () => {
  const onAnswer = vi.fn();
  const { container } = render(<TaskPicture problem={{ ...add, skill: 'odd_even', operation: 'parity', kind: 'parity', operand_a: 5, operand_b: 0, prompt: { value: 5 } }} theme="flowers" picture onAnswer={onAnswer} disabled={false} />);
  expect(container.querySelectorAll('[data-pair]').length).toBe(3);
  fireEvent.click(screen.getByRole('button', { name: 'Нет' }));
  expect(onAnswer).toHaveBeenCalledWith(1);  // 1 = odd: not everyone has a partner
});

test('neighbour draws carriages with one empty; missing hides the blanked objects behind a garage', () => {
  const { container } = render(<TaskPicture problem={{ ...add, skill: 'neighbour_one', operand_a: 4, operand_b: 1, prompt: null }} theme="cars" picture disabled={false} onAnswer={() => {}} />);
  expect(container.querySelectorAll('[data-carriage]').length).toBe(3);
  expect(container.querySelector('[data-carriage="empty"]')).toBeTruthy();
  const { container: garage } = render(<TaskPicture problem={{ ...add, kind: 'missing', operand_a: 3, operand_b: null, prompt: { blank: 'b', result: 5, options: [1, 2, 3] } }} theme="cars" picture disabled={false} onAnswer={() => {}} />);
  expect(garage.querySelector('[data-garage]')).toBeTruthy();
});
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `(cd frontend && npx vitest run src/features/game/TaskPicture.test.tsx)`
Expected: FAIL — `picture` prop unknown, no piles rendered.

- [ ] **Step 3: Implement the layers**

`pictureKind(problem, picture)`: returns `null` when `!picture`; `'compare'` for kind `compare` with both operands ≤ 10; `'parity'` for kind `parity` with `prompt.value ≤ 10`; `'neighbour'` for skill `neighbour_one` with `operand_a ≤ 10`; the existing `add`/`sub`/`missing` rules stay. Rendering with `ThemeIcon`:

- compare: two `<button aria-label="Кучка 1|2">` each with `operand` icons; tapping pile 1 submits `1` if `a > b`… **no** — the child taps the pile they believe is larger, so pile 1 submits `1` and pile 2 submits `-1`; the "Одинаково"/"Same" card submits `0`. The server grades.
- parity: `Math.ceil(value / 2)` `<span data-pair>` rows of two icons, the last with one icon when odd; cards «Да» → `0` (even, everyone has a partner) and «Нет» → `1`.
- neighbour: `operand_a` … draw three carriages `a-1, a, a+1` where the one that equals the correct answer position is empty: for `neighbour_one` the task is `a + 1` or `a − 1`; draw `[a−1, a, a+1]` with the carriage at the asked side empty (`operation === 'addition'` → the right one), numerals on the other two; answer comes through the number cards (`options`) rendered by `EarlyTask`.
- missing: keep the existing known objects; wrap the empty slots in `<span data-garage className={styles.garage}>` drawn as a roof and door with the count hidden.
- subtraction: the removed icons get `styles.leaving` (600 ms `transform: translateX(120%)` + `opacity: .2`, disabled under `@media (prefers-reduced-motion: reduce)`).
- addition: both groups inside `<span data-basket className={styles.basket}>`.

`GamePage.tsx`: `<TaskPicture problem={problem} theme={player.theme} picture={picture} disabled={status !== 'ready'} onAnswer={submitValue} />` and, when `picture && (problem.kind === 'compare' || problem.kind === 'parity')`, skip `ChoicePad`. i18n: `early.pile` «Кучка» / "Pile", `early.same` «Одинаково» / "Same", `early.yes` «Да» / "Yes", `early.no` «Нет» / "No", `prompt.parityPicture` «Всем хватило пары?» / "Did everyone get a partner?", `prompt.comparePicture` «Где больше?» / "Which has more?".

- [ ] **Step 4: Run typecheck and vitest**

Run: `(cd frontend && npm run typecheck && npx vitest run)`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add frontend/src/features/game/TaskPicture.tsx frontend/src/features/game/TaskPicture.test.tsx frontend/src/features/game/TaskPicture.module.css frontend/src/features/game/GamePage.tsx frontend/src/features/game/prompt.ts frontend/src/i18n.tsx
git commit -m "feat(ui): draw compare, parity, neighbour, garage, leaving and basket scenes for young children"
```

### Task 6: Speech, SVG Assets, Stickers and Parent Controls

**Files:**
- Create: `frontend/src/features/game/early/useSpeech.ts`, `useSpeech.test.ts`
- Modify: `frontend/src/assets/themes/index.tsx`; create `flowers.tsx`, `dolls.tsx`, `cars.tsx`, `construction.tsx`, `shared.tsx`, `ASSETS.md`
- Modify: `frontend/src/features/game/SessionSummary.tsx`, `ChildHome.tsx`, `GamePage.tsx`, `players/PlayerSettings.tsx`, `players/PlayerPicker.tsx`, `frontend/src/i18n.tsx`, `frontend/src/styles.css`
- Modify: `scripts/check_assets.py`

**Interfaces:**
- Consumes: `ProgressView.rewards` (Task 3), `PlayerView.round_tasks` (Task 2).
- Produces: `useSpeech(): { speak(text: string): void; supported: boolean }`; `Sticker({ code, className })` in `assets/themes/index.tsx` mapping `<theme>-<n>`; `ThemeIcon` now renders SVG (same props as Task 4).

- [ ] **Step 1: Write the failing tests**

```ts
// frontend/src/features/game/early/useSpeech.test.ts
import { renderHook } from '@testing-library/react';
import { afterEach, expect, test, vi } from 'vitest';
import { useSpeech } from './useSpeech';

afterEach(() => { vi.unstubAllGlobals(); });

test('without speechSynthesis the hook is silent and reports unsupported', () => {
  vi.stubGlobal('speechSynthesis', undefined);
  const { result } = renderHook(() => useSpeech('ru'));
  expect(result.current.supported).toBe(false);
  expect(() => result.current.speak('Сколько?')).not.toThrow();
});

test('with a matching voice the hook cancels the previous utterance and speaks in the current language', () => {
  const speak = vi.fn(), cancel = vi.fn();
  vi.stubGlobal('speechSynthesis', { speak, cancel, getVoices: () => [{ lang: 'ru-RU', name: 'Milena' }, { lang: 'en-GB', name: 'Daniel' }] });
  vi.stubGlobal('SpeechSynthesisUtterance', class { text: string; lang = ''; voice: unknown = null; constructor(text: string) { this.text = text; } });
  const { result } = renderHook(() => useSpeech('ru'));
  result.current.speak('Сколько машинок?');
  expect(cancel).toHaveBeenCalled();
  expect(speak.mock.calls[0][0]).toMatchObject({ text: 'Сколько машинок?', lang: 'ru-RU' });
});
```

Add to `SessionSummary` a test that with `rewards.count = 3` and theme `cars` the sticker `cars-3` is shown, and to `PlayerSettings` a test that the form posts `round_tasks` and the `early` checkbox.

- [ ] **Step 2: Run the tests to verify they fail**

Run: `(cd frontend && npx vitest run src/features/game/early/useSpeech.test.ts)`
Expected: FAIL — `Cannot find module './useSpeech'`.

- [ ] **Step 3: Implement speech**

```ts
// frontend/src/features/game/early/useSpeech.ts
import { useCallback, useMemo } from 'react';
import type { Lang } from '../../../i18n';

const LOCALE: Record<Lang, string> = { ru: 'ru-RU', en: 'en-GB' };

/** Browser speech only; silent when the API or a matching voice is missing. Never records anything. */
export function useSpeech(lang: Lang) {
  const synth = typeof speechSynthesis === 'undefined' ? null : speechSynthesis;
  const voice = useMemo(() => synth?.getVoices().find(item => item.lang.replace('_', '-').toLowerCase().startsWith(lang)) ?? null, [synth, lang]);
  const speak = useCallback((text: string) => {
    if (!synth || typeof SpeechSynthesisUtterance === 'undefined') return;
    synth.cancel();
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = LOCALE[lang];
    if (voice) utterance.voice = voice as SpeechSynthesisVoice;
    utterance.rate = 0.9;
    synth.speak(utterance);
  }, [synth, voice, lang]);
  return { speak, supported: synth !== null };
}
```

`GamePage.tsx`: in picture mode, `useEffect(() => { if (picture && problem && answering) speak(spokenPrompt); }, [problem?.id, answering])` where `spokenPrompt = parts.join('')` for early kinds and `t('speak.expression', { expression })` for numeric ones (ru «Сколько будет {expression}?» / en "What is {expression}?"); after feedback speak `t(snapshot.feedback.correct ? 'game.correct' : 'game.wrong')`. A `<button className="secondary" aria-label={t('early.repeat')}>🔊</button>` repeats. iOS: the first `speak` happens after the child's tap on "Начать"/"Start" (the route change is a gesture), so no extra unlock step.

- [ ] **Step 4: Draw the SVG set and the stickers**

Each theme file exports `OBJECTS: JSX.Element[]` (4 objects as `<g>` bodies in a 100×100 viewBox), `SCENES: { basket, garage, train, tray }` and `STICKERS: JSX.Element[8]`; `shared.tsx` exports `SHAPES` and `DOTS`. Simple flat shapes: flowers (daisy, tulip, sunflower, leaf), dolls (doll, bow, bear, balloon), cars (car, bus, truck, bike), construction (excavator, cone, crane, brick). `index.tsx` renders `<svg viewBox="0 0 100 100" className aria-hidden="true">{OBJECTS[theme][icon % 4]}</svg>`; `Sticker({ code })` splits `code` into theme and index. `ASSETS.md` states: drawn by hand for this repository, licensed with the repository, no third-party artwork. Keep each theme file under 12 KB of source.

- [ ] **Step 5: Sticker on the summary, shelf on the child home, parent controls**

`SessionSummary`: fetch `api<ProgressView>(`/players/${player.id}/progress?limit=1`)` on mount; when `snapshot.answered_count * 2 >= snapshot.total_problems` and `rewards.latest` exists, render `<Sticker code={rewards.latest} className="sticker-new" />` with the text `t('summary.sticker')` («Новая наклейка!» / "A new sticker!"). `ChildHome`: fetch progress once and render `<ul className="shelf">` with `Array.from({ length: Math.min(rewards.count, 8) }, (_, i) => <Sticker code={`${player.theme}-${i + 1}`} />)` plus `t('home.stickers', { n: rewards.count })` («Наклеек: {n}» / "Stickers: {n}"). `PlayerSettings`: add `'early'` to `TOPICS` and a select `round_tasks` with 6/10 (`settings.round` «Задач в раунде» / "Tasks per round"); include `round_tasks: Number(form.get('round_tasks'))` in the PATCH body. `PlayerPicker`: stop sending `topics` so the server resolves the age-based default.

- [ ] **Step 6: Bundle budget in `check_assets.py`**

```python
import gzip
BUDGET_GZIP_BYTES = 160 * 1024
...
    compressed = sum(len(gzip.compress(path.read_bytes())) for path in (DIST / "assets").glob("*") if path.suffix in {".js", ".css"})
    print(f"bundle gzip: {compressed} bytes (budget {BUDGET_GZIP_BYTES})")
    if compressed > BUDGET_GZIP_BYTES:
        findings.append((Path("assets"), f"bundle gzip {compressed} exceeds {BUDGET_GZIP_BYTES}"))
```

- [ ] **Step 7: Run the checks**

```bash
(cd frontend && npm run typecheck && npx vitest run && npm run build)
uv run --project backend python scripts/check_assets.py
```

Expected: PASS; `check_assets.py` prints the gzip size under 163 840 bytes.

- [ ] **Step 8: Commit**

```bash
git add frontend/src/assets frontend/src/features/game/early/useSpeech.ts frontend/src/features/game/early/useSpeech.test.ts frontend/src/features/game/SessionSummary.tsx frontend/src/features/game/ChildHome.tsx frontend/src/features/game/GamePage.tsx frontend/src/features/players frontend/src/i18n.tsx frontend/src/styles.css scripts/check_assets.py
git commit -m "feat(ui): speak tasks, draw theme SVG objects and stickers, let parents choose round length and the early topic"
```

### Task 7: Browser Journeys, GWT Scenarios and Documentation

**Files:**
- Create: `frontend/e2e/early-round.spec.ts`; modify `frontend/e2e/helpers.ts` (`registerWithChild` age default unchanged; add `solveEarly(page)`), `frontend/e2e/pictures.spec.ts` (round of 6 for age 5)
- Modify: `README.md`, `docs/README.ru.md` (if present), `docs/runbooks/release-checklist.md`
- Wiki (parent session): `specification/skill-practice` (+4 scenarios, extended `task-shapes-solvable-from-public-prompt`), `architecture/mental-math-web-platform` («Child Flow and Progress»), task ledger

**Interfaces:**
- Consumes: everything above.
- Produces: green `npm run test:e2e`; scenarios `early-round-playable-by-tapping`, `answer-options-never-mark-the-correct-card`, `round-length-follows-profile`, `theme-reward-derived-from-finished-rounds`.

- [ ] **Step 1: Write the Playwright journeys**

```ts
// frontend/e2e/early-round.spec.ts
import { expect, test, type Page } from '@playwright/test';
import { registerWithChild } from './helpers';

/** Solves any picture-mode task from what is on screen — the same way a child would, by tapping. */
async function solveByTapping(page: Page) {
  const objects = page.locator('[data-object] >> visible=true');
  if (await page.getByRole('button', { name: 'Готово' }).isVisible()) {
    const buttons = page.getByRole('button', { name: /Предмет \d/ });
    const count = await buttons.count();
    if (count > 0) { for (let i = 0; i < count; i++) await buttons.nth(i).click(); }
    else { const n = await page.locator('.task-scene [data-object]').count(); for (let i = 0; i < n; i++) await page.getByRole('button', { name: 'Добавить' }).click(); }
    await page.getByRole('button', { name: 'Готово' }).click();
    return;
  }
  if (await page.getByRole('button', { name: /Башня 1/ }).isVisible()) {
    const towers = page.getByRole('button', { name: /Башня \d/ });
    const heights: number[] = [];
    for (let i = 0; i < await towers.count(); i++) heights.push(await towers.nth(i).locator('svg').count());
    for (const index of [...heights.keys()].sort((a, b) => heights[a] - heights[b])) await towers.nth(index).click();
    return;
  }
  if (await page.getByRole('button', { name: /Фигура 1/ }).isVisible()) {
    const target = await page.locator('.expression').innerText();
    // the e2e run only needs a graded answer: tap the first item, the server decides correctness
    await page.getByRole('button', { name: /Фигура 1/ }).click();
    return void target;
  }
  if (await page.getByRole('button', { name: /Кучка 1/ }).isVisible()) { await page.getByRole('button', { name: /Кучка 1/ }).click(); return; }
  if (await page.getByRole('button', { name: 'Да' }).isVisible()) { await page.getByRole('button', { name: 'Да' }).click(); return; }
  await page.getByRole('button', { name: /Карточка 1/ }).click();
  void objects;
}

test('a four-year-old plays a six-task round by taps only, gets a sticker and starts again', async ({ page }) => {
  await registerWithChild(page, 'early', '4');
  await page.getByRole('link', { name: 'Начать' }).click();
  for (let task = 1; task <= 6; task++) {
    await expect(page.getByRole('heading', { name: `Задача ${task} из 6` })).toBeVisible();
    await expect(page.getByRole('group', { name: 'Клавиатура' })).toHaveCount(0);  // never the keypad
    await solveByTapping(page);
    await page.getByRole('button', { name: 'Дальше' }).click();
  }
  await expect(page.getByRole('heading', { name: 'Занятие завершено' })).toBeVisible();
  await expect(page.locator('.sticker-new')).toBeVisible();
  await page.getByRole('button', { name: 'Ещё!' }).click();
  await expect(page.getByRole('heading', { name: 'Задача 1 из 6' })).toBeVisible();
});

test('a seven-year-old still sees the number pad and ten tasks', async ({ page }) => {
  await registerWithChild(page, 'older', '7');
  await page.getByRole('link', { name: 'Начать' }).click();
  await expect(page.getByRole('heading', { name: 'Задача 1 из 10' })).toBeVisible();
  await expect(page.getByRole('group', { name: 'Клавиатура' })).toBeVisible();
  await expect(page.locator('.task-picture')).toHaveCount(0);
});
```

Check the feedback button's label in `Feedback.tsx` (`game.next` or similar) and use its Russian text in place of «Дальше». Update `pictures.spec.ts` to expect «Задача 1 из 6» for the age-5 child.

- [ ] **Step 2: Run Playwright alone (not concurrently with pytest)**

```bash
docker compose -f compose.test.yaml up -d --wait postgres-test
(cd frontend && npm run test:e2e)
```

Expected: all specs pass, including the two new journeys.

- [ ] **Step 3: Documentation**

README (English) and `docs/README.ru.md` (Russian, if the file exists): topic «Малышам»/`early` with the nine game forms, picture mode for ages 4–5 (cards instead of the keypad, spoken prompts, theme SVG objects), parent-chosen round length 6/10, stickers derived from finished rounds, the bundle budget and the 15 task kinds. `docs/runbooks/release-checklist.md`: a row for the bundle budget check and the speech smoke on a phone.

- [ ] **Step 4: GWT scenarios (parent session, wiki)**

On `specification/skill-practice` (read the page first, pass `expected_revision`), append four `##` sections with one `iwiki-gwt` fence each:

```toml
id = "early-round-playable-by-tapping"
title = "Early round playable by tapping"
given = [{ role = "state", name = "ProfileAgedFourWithTopicEarlyAndSixTaskRounds" }]
when = { role = "action", name = "ChildAnswersEveryTaskByTappingScenesOrCards" }
then = [
  { role = "outcome", name = "RoundOfSixFinishesWithoutKeypadOrReadableText" },
  { role = "outcome", name = "AtLeastTwoDistinctEarlyKindsIssued" }
]
code = [
  { relation = "implements", phase = "given", symbol = "mental_math.game.engine.start_session" },
  { relation = "implements", phase = "when", symbol = "mental_math.game.catalogue.generate" },
  { relation = "verifies", file = "backend/tests/integration/test_early_sessions.py" },
  { relation = "verifies", file = "frontend/e2e/early-round.spec.ts" }
]
```

```toml
id = "answer-options-never-mark-the-correct-card"
title = "Answer options never mark the correct card"
given = [{ role = "state", name = "PictureModeSessionOrEarlySkillWithOptions" }]
when = { role = "request", name = "ReadPublicProblem" }
then = [
  { role = "outcome", name = "ThreeDistinctOptionsHoldTheAnswerOnceInAUniformPosition" },
  { role = "outcome", name = "NoOtherTopLevelPromptNumberEqualsTheAnswer" }
]
code = [
  { relation = "implements", phase = "then", symbol = "mental_math.game.early.answer_options" },
  { relation = "implements", phase = "when", symbol = "mental_math.game.engine.public_problem" },
  { relation = "verifies", file = "backend/tests/unit/test_early_catalogue.py" },
  { relation = "verifies", file = "backend/tests/unit/test_public_view_hides_answers.py" }
]
```

```toml
id = "round-length-follows-profile"
title = "Round length follows the profile"
given = [{ role = "state", name = "ProfileWithRoundTasksSixOrTen" }]
when = { role = "request", name = "StartSession" }
then = [
  { role = "response", name = "SnapshotTotalProblemsEqualsProfileRoundTasks" },
  { role = "outcome", name = "SessionFinishesAfterThatManyAnswers" }
]
code = [
  { relation = "implements", phase = "when", symbol = "mental_math.game.engine.start_session" },
  { relation = "implements", phase = "then", symbol = "mental_math.game.engine.round_length" },
  { relation = "verifies", file = "backend/tests/integration/test_early_sessions.py" }
]
```

```toml
id = "theme-reward-derived-from-finished-rounds"
title = "Theme reward derived from finished rounds"
given = [{ role = "state", name = "ChildWithFinishedAndAbandonedRounds" }]
when = { role = "request", name = "ReadProgress" }
then = [
  { role = "response", name = "RewardsCountRoundsWithAtLeastHalfAnsweredAndLatestStickerCode" }
]
code = [
  { relation = "implements", phase = "then", symbol = "mental_math.players.rewards.rewards_for" },
  { relation = "implements", phase = "when", symbol = "mental_math.players.routes.progress" },
  { relation = "verifies", file = "backend/tests/integration/test_rewards.py" }
]
```

Update the lead of «Task shapes and independent solvability» from "47 skills" to "59 skills and fifteen kinds", keep the scenario id, and add `{ relation = "verifies", file = "backend/tests/unit/test_early_catalogue.py" }`. Update the architecture page paragraph («Child Flow and Progress») for the topic, picture mode, round length and rewards. Then `wiki_code_index` (local) → `wiki_code_refresh_links` → `wiki_spec_resolve` for the five scenarios → `wiki_lint`.

- [ ] **Step 5: Full verification and commit**

```bash
uv run --project backend pytest -q
(cd frontend && npm run typecheck && npx vitest run && npm run build)
uv run --project backend python scripts/check_contract.py
uv run --project backend python scripts/check_assets.py
(cd frontend && npm run test:e2e)
git diff --check
git add frontend/e2e README.md docs
git commit -m "test(e2e): play an early round by taps and document the early numeracy topic"
```

Expected: every command exits 0; record counts in the ledger.

### Task 8: Deployment to minipc and Post-Deployment Checks (S7)

**Files:**
- Modify: `docs/runbooks/deployment.md` (a line recording the early-numeracy deployment)
- Host: `/opt/mmath/src` (git pull to the branch head), compose project `mmath`

**Interfaces:**
- Consumes: the whole branch.
- Produces: live deployment, measured metrics, ledger events.

- [ ] **Step 1: Ask the owner** — post «Деплой на minipc: ветка dev-early-numeracy-game-tasks @ <sha>, миграция 0010. ок?» and wait for «ок» (proposal-first per the intent).

- [ ] **Step 2: Deploy**

```bash
ssh minipc 'git -C /opt/mmath/src fetch origin && git -C /opt/mmath/src checkout dev-early-numeracy-game-tasks && git -C /opt/mmath/src pull --ff-only'
ssh minipc '/opt/mmath/src/deploy/minipc-lan.sh config && /opt/mmath/src/deploy/minipc-lan.sh up'
ssh minipc '/opt/mmath/src/deploy/minipc-lan.sh ps'
```

Expected: `migrate` exits 0 with `0010_early_numeracy` applied, `api` healthy, `web` published on `192.168.68.135:8080`.

- [ ] **Step 3: Post-deployment checks**

```bash
ssh minipc 'docker exec mmath-api-1 python -c "import urllib.request;print(urllib.request.urlopen(\"http://127.0.0.1:8000/health/ready\").read().decode())"'
curl -s -o /dev/null -w '%{http_code}\n' http://192.168.68.135:8080/
uv run --project backend python scripts/check_deployment.py --base-url http://192.168.68.135:8080 --age 4 --rounds 2
```

If `check_deployment.py` has no `--base-url/--age/--rounds` options, run the equivalent synthetic journey with `curl` as in S15: register a synthetic parent, create an age-4 child (expect `topics` to include `early`, `round_tasks` 6), start a session (expect `picture_mode` true, `total_problems` 6), answer six tasks with the solver of `backend/tests/conftest.py`, finish, read progress (expect `rewards.count` 1) — then a second round (expect `rewards.count` 2 and `latest` `<theme>-2`). Record the synthetic account e-mail in the ledger for later removal.

- [ ] **Step 4: Measure the metrics**

```bash
ssh minipc 'docker logs mmath-api-1 2>&1 | grep "\"route\": \"/api/v1/sessions\"" | grep "\"method\": \"POST\"" | grep -o "\"duration_ms\": [0-9]*" | awk -F": " "{print \$2}" | sort -n | awk "{a[NR]=\$1} END {print \"n=\"NR\" p50=\"a[int((NR+1)/2)]\" p95=\"a[int(NR*0.95+0.999)]\" max=\"a[NR]}"'
uv run --project backend python scripts/check_assets.py
```

Expected: `n ≥ 20`, `p95 ≤ 60`; bundle gzip ≤ 163 840 bytes. Any miss is a finding recorded in the ledger, not silently accepted.

- [ ] **Step 5: Record**

Append a `verification` event (S7) with the commands, exit codes and the measured numbers; update `docs/runbooks/deployment.md` with the date and revision; commit `docs(deploy): record the early numeracy deployment on minipc`. S8 (supervised child check) stays open as a human checkpoint; the topic stays `completion-pending` until PR #1 merges, this branch is rebased and its PR opened.
