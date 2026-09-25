"""Pure mastery calculation; versioned so stored values can be recomputed when the formula changes."""

from dataclasses import dataclass

FORMULA_VERSION = "mastery-v1-10s"
TARGET_MS = 10_000
WINDOW = 20


def calculate_mastery(*, recent_accuracy: float, speed_score: float, consistency: float) -> float:
    return min(1.0, max(0.0, 0.50 * recent_accuracy + 0.30 * speed_score + 0.20 * consistency))


@dataclass(frozen=True)
class WindowSummary:
    recent_accuracy: float
    speed_score: float
    consistency: float
    mastery: float


def summarize_window(window: list[dict]) -> WindowSummary | None:
    """Unknown before the first attempt. Speed counts only correct, unhinted attempts with a valid sample."""
    if not window:
        return None
    recent = window[-WINDOW:]
    correct = [item for item in recent if item["correct"]]
    unhinted_correct = [item for item in correct if not item["hinted"]]
    timed = [item["response_ms"] for item in unhinted_correct if item["response_ms"] is not None and item["response_ms"] > 0]
    recent_accuracy = len(correct) / len(recent)
    consistency = len(unhinted_correct) / len(recent)
    speed_score = min(1.0, TARGET_MS / (sum(timed) / len(timed))) if timed else 0.0
    return WindowSummary(recent_accuracy, speed_score, consistency, calculate_mastery(recent_accuracy=recent_accuracy, speed_score=speed_score, consistency=consistency))
