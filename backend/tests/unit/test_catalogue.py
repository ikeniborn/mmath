from uuid import uuid4

import pytest

from mental_math.game.catalogue import CATALOGUE, eligible_pairs, generate, supported_bands


@pytest.mark.parametrize("code", sorted(CATALOGUE))
def test_every_skill_band_pair_keeps_bounds_and_deterministic_answers(code):
    entry = CATALOGUE[code]
    assert entry.bands, code
    for band in entry.bands:
        for ordinal in range(200):
            problem = generate(code, uuid4(), ordinal, band)
            assert problem.skill == code and problem.band == band and (entry.operation == "mixed" or problem.operation == entry.operation)
            assert problem.operand_a >= 0 and problem.operand_b >= 0
            assert entry.check(problem), (code, band, problem)
            if problem.kind == "result" and entry.operation == "addition":
                assert problem.correct_answer == problem.operand_a + problem.operand_b
            elif problem.kind == "result" and entry.operation == "subtraction":
                assert problem.correct_answer == problem.operand_a - problem.operand_b >= 0
            elif problem.kind == "result" and entry.operation == "multiplication":
                assert problem.correct_answer == problem.operand_a * problem.operand_b
            elif problem.kind == "result" and entry.operation == "division":
                assert problem.correct_answer == problem.operand_a // problem.operand_b
            elif problem.kind == "missing":
                expected = {"addition": problem.operand_a + problem.operand_b, "subtraction": problem.operand_a - problem.operand_b, "multiplication": problem.operand_a * problem.operand_b}[entry.operation]
                assert problem.prompt["result"] == expected and problem.correct_answer == (problem.operand_a if problem.prompt["blank"] == "a" else problem.operand_b)
            elif problem.kind == "chain":
                assert problem.correct_answer == sum(problem.prompt["terms"])


def test_band_semantics_of_the_baseline_skills():
    session = uuid4()
    for ordinal in range(100):
        add2 = generate("addition", session, ordinal, 2)
        assert add2.operand_a <= 9 and add2.operand_b <= 9 and 11 <= add2.correct_answer <= 20
        sub2 = generate("subtraction", session, ordinal, 2)
        assert sub2.operand_a > 10 > sub2.correct_answer >= 1 and sub2.operand_b <= 9
        sub4 = generate("subtraction", session, ordinal, 4)
        assert 0 <= sub4.correct_answer <= sub4.operand_a <= 50
        assert generate("doubles", session, ordinal, 3).operand_a == generate("doubles", session, ordinal, 3).operand_b
        near = generate("near_doubles", session, ordinal, 3)
        assert abs(near.operand_a - near.operand_b) == 1
        assert generate("make_ten", session, ordinal, 1).correct_answer == 10
        assert generate("multiplication_2", session, ordinal, 3).operand_b == 2
        assert generate("multiplication_3", session, ordinal, 4).operand_b == 3 and generate("multiplication_3", session, ordinal, 4).correct_answer <= 30


def test_generation_is_deterministic_per_session_ordinal_skill_band():
    session = uuid4()
    first, second = generate("subtraction", session, 7, 3), generate("subtraction", session, 7, 3)
    assert (first.operand_a, first.operand_b) == (second.operand_a, second.operand_b)


def test_fixed_mode_eligibility_reports_supported_alternatives():
    assert eligible_pairs(["multiplication"], "fixed", 0) == []
    assert supported_bands(["multiplication"]) == [2, 3, 4]
    assert supported_bands(["addition", "multiplication"]) == [0, 1, 2, 3, 4]
    pairs = eligible_pairs(["addition"], "fixed", 1)
    assert ("addition", 1) in pairs and ("make_ten", 1) in pairs and ("doubles", 1) in pairs
    assert all(band == 1 for _, band in pairs)
    assert ("multiplication_2", 2) not in eligible_pairs(["addition"], "fixed", 2)


def test_research_families_have_the_expected_shapes():
    session = uuid4()
    for ordinal in range(60):
        bond = generate("number_bonds", session, ordinal, 4)
        assert bond.kind == "missing" and bond.prompt["result"] == 100
        chain = generate("chain_add", session, ordinal, 4)
        assert chain.kind == "chain" and len(chain.prompt["terms"]) == 4 and any(term < 0 for term in chain.prompt["terms"]) and 0 <= chain.correct_answer <= 100
        seq = generate("skip_counting", session, ordinal, 2)
        assert seq.kind == "sequence" and seq.prompt["step"] == 5 and seq.prompt["terms"] == [seq.prompt["terms"][0] + i * 5 for i in range(3)]
        assert generate("odd_even", session, ordinal, 1).correct_answer in {0, 1}
        op = generate("missing_operator", session, ordinal, 4)
        a, b, result = op.operand_a, op.operand_b, op.prompt["result"]
        assert [a + b, a - b, a * b][op.correct_answer] == result
        cmp = generate("compare", session, ordinal, 3)
        assert cmp.kind == "compare" and cmp.correct_answer == (-1 if cmp.operand_a < cmp.operand_b else 1 if cmp.operand_a > cmp.operand_b else 0)
        assert "+" in cmp.prompt["left"] or "−" in cmp.prompt["left"]
        rem = generate("remainder", session, ordinal, 4)
        assert rem.correct_answer == rem.operand_a % rem.operand_b
        assert generate("multiply_by_10", session, ordinal, 4).correct_answer <= 1000
        assert generate("two_digit_divide", session, ordinal, 4).operand_a % generate("two_digit_divide", session, ordinal, 4).operand_b == 0
        assert generate("multiplication_7", session, ordinal, 4).operand_b == 7 and generate("division_8", session, ordinal, 3).operand_b == 8


def test_catalogue_covers_every_topic_and_no_word_problems():
    from mental_math.game.catalogue import TOPICS
    assert set(TOPICS) == {skill.topic for skill in CATALOGUE.values()}
    assert len(CATALOGUE) >= 40
    assert all(set(supported_bands([topic])) for topic in TOPICS)


def test_missing_operator_tasks_have_exactly_one_valid_operator():
    from mental_math.game.catalogue import missing_operator
    import random

    rng = random.Random(2026)
    for band in (1, 3, 4):
        offered = 3 if band == 4 else 2
        for _ in range(5000):
            problem = missing_operator(rng, band)
            a, b, result = problem.operand_a, problem.operand_b, problem.prompt["result"]
            candidates = [a + b, a - b, a * b][:offered]
            assert candidates.count(result) == 1 and candidates.index(result) == problem.correct_answer, (a, b, result)


def test_no_degenerate_zero_operands_and_no_missing_zero():
    session = uuid4()
    for code, skill in CATALOGUE.items():
        for band in skill.bands:
            for ordinal in range(1, 301):
                p = generate(code, session, ordinal, band)
                if p.kind == "missing":
                    assert p.correct_answer != 0, (code, band, p)
                if p.kind == "result" and p.operation in {"addition", "subtraction"}:
                    assert not (p.operand_a == 0 and p.operand_b == 0), (code, band, p)
                    if band >= 1:
                        assert p.operand_a != 0 and p.operand_b != 0, (code, band, p)
                    if p.operation == "subtraction":
                        assert p.operand_b >= 1, (code, band, p)
