import pytest

from mental_math.student.mastery import FORMULA_VERSION, TARGET_MS, calculate_mastery, summarize_window


def test_mastery_known_window():
    value = calculate_mastery(recent_accuracy=0.5, speed_score=1.0, consistency=0.25)
    assert value == pytest.approx(0.60)


def test_mastery_is_clamped():
    assert calculate_mastery(recent_accuracy=1.0, speed_score=1.0, consistency=1.0) == 1.0
    assert calculate_mastery(recent_accuracy=0.0, speed_score=0.0, consistency=0.0) == 0.0


def test_worked_example_from_independent_calculation():
    window = [
        {"correct": True, "hinted": False, "response_ms": 5_000},
        {"correct": True, "hinted": True, "response_ms": 3_000},
        {"correct": False, "hinted": False, "response_ms": 20_000},
        {"correct": True, "hinted": False, "response_ms": 15_000},
    ]
    summary = summarize_window(window)
    assert summary.recent_accuracy == pytest.approx(0.75)
    assert summary.consistency == pytest.approx(0.5)
    assert summary.speed_score == pytest.approx(min(1.0, TARGET_MS / 10_000))
    assert summary.mastery == pytest.approx(0.5 * 0.75 + 0.3 * 1.0 + 0.2 * 0.5)
    assert FORMULA_VERSION.startswith("mastery-v1")


def test_unknown_before_first_attempt_and_invalid_timing_cannot_raise_speed():
    assert summarize_window([]) is None
    only_invalid = summarize_window([{"correct": True, "hinted": False, "response_ms": None}])
    assert only_invalid.speed_score == 0.0
    assert only_invalid.mastery == pytest.approx(0.5 + 0.2)
    fast_hinted = summarize_window([{"correct": True, "hinted": True, "response_ms": 100}])
    assert fast_hinted.speed_score == 0.0 and fast_hinted.consistency == 0.0
