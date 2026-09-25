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
            assert problem.skill == code and problem.band == band and problem.operation == entry.operation
            assert problem.operand_a >= 0 and problem.operand_b >= 0
            assert entry.check(problem.operand_a, problem.operand_b, band), (code, band, problem)
            if entry.operation == "addition":
                assert problem.correct_answer == problem.operand_a + problem.operand_b
            elif entry.operation == "subtraction":
                assert problem.correct_answer == problem.operand_a - problem.operand_b >= 0
            else:
                assert problem.correct_answer == problem.operand_a * problem.operand_b


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
