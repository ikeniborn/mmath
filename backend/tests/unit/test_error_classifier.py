from dataclasses import dataclass

import pytest

from mental_math.student.errors import classify


@dataclass
class P:
    operation: str
    operand_a: int
    operand_b: int
    correct_answer: int


@pytest.mark.parametrize("answer, expected", [(15, None), (14, "off_by_one"), (16, "off_by_one"), (87, "concatenation"), (78, "concatenation"), (1, "subtraction_confusion"), (99, "other")])
def test_lld_examples_for_eight_plus_seven(answer, expected):
    assert classify(P("addition", 8, 7, 15), answer) == expected


def test_precedence_is_correctness_off_by_one_concatenation_subtraction_confusion():
    assert classify(P("addition", 9, 1, 10), 11) == "off_by_one"
    assert classify(P("addition", 9, 1, 10), 91) == "concatenation"
    assert classify(P("addition", 9, 1, 10), 8) == "subtraction_confusion"
    # 1 + 0 = 1: 10 is a concatenation, and 0 is both off-by-one and |a-b|; off-by-one wins.
    assert classify(P("addition", 1, 0, 1), 10) == "concatenation"
    assert classify(P("addition", 1, 0, 1), 0) == "off_by_one"


def test_operations_are_checked_explicitly():
    assert classify(P("subtraction", 12, 5, 7), 17) == "subtraction_confusion"
    assert classify(P("subtraction", 12, 5, 7), 125) == "concatenation"
    assert classify(P("multiplication", 3, 2, 6), 5) == "off_by_one"
    assert classify(P("multiplication", 3, 2, 6), 32) == "concatenation"
    assert classify(P("multiplication", 3, 2, 6), 1) == "other"
    assert classify(P("multiplication", 3, 2, 6), 6) is None
