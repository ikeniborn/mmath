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
