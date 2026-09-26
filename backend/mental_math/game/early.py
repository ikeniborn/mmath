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
    a, b, c = rng.sample(range(ICONS), 3)
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


SKILLS = (("count_objects", count_objects), ("make_same", make_same), ("quick_look", quick_look), ("what_next", what_next), ("five_frame", five_frame), ("order_size", order_size), ("share_equal", share_equal), ("find_shape", find_shape), ("pick_size", pick_size))
