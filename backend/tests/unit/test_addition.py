from uuid import uuid4

import pytest

from mental_math.game.generator import BAND_LIMITS, generate_addition
from mental_math.game.validator import grade


@pytest.mark.parametrize("band", sorted(BAND_LIMITS))
def test_addition_operands_and_results_stay_within_band_bounds(band):
    for ordinal in range(300):
        problem = generate_addition(uuid4(), ordinal, band)
        assert problem.operation == "addition"
        assert problem.band == band
        assert problem.operand_a >= 0 and problem.operand_b >= 0
        assert problem.correct_answer == problem.operand_a + problem.operand_b
        low, high = BAND_LIMITS[band]
        assert low <= problem.correct_answer <= high
        if band == 0:
            assert problem.operand_a <= 5 and problem.operand_b <= 5
        if band == 2:
            assert problem.operand_a <= 9 and problem.operand_b <= 9


def test_generation_is_deterministic_for_session_and_ordinal():
    session_id = uuid4()
    first = generate_addition(session_id, 3, 0)
    second = generate_addition(session_id, 3, 0)
    assert (first.operand_a, first.operand_b) == (second.operand_a, second.operand_b)


def test_grade_is_exact():
    problem = generate_addition(uuid4(), 0, 0)
    assert grade(problem, problem.correct_answer) is True
    assert grade(problem, problem.correct_answer + 1) is False
