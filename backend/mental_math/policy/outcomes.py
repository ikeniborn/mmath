"""Outcome assembly for policy decisions, derived on demand from committed attempts and sessions.

Windows count only subsequent accepted attempts of the same child and skill; an unfinished window is
marked incomplete rather than treated as failure or success, and the return signal needs a later session.
"""

from dataclasses import dataclass
from datetime import datetime, timedelta

WINDOW = 5
RETURN_OBSERVATION = timedelta(days=7)


@dataclass(frozen=True)
class AttemptFact:
    attempt_id: str
    created_at: datetime
    correct: bool
    response_ms: int | None


def window_summary(facts: list[AttemptFact]) -> dict:
    timed = [fact.response_ms for fact in facts if fact.response_ms is not None and fact.response_ms > 0]
    return {"count": len(facts), "accuracy": (sum(fact.correct for fact in facts) / len(facts)) if facts else None, "avg_time_ms": (sum(timed) / len(timed)) if timed else None}


def build_outcome(history: list[AttemptFact], attempt_id: str, session_state: str, session_started_at: datetime, later_session_started: bool, now: datetime) -> dict:
    """history: every accepted attempt of the same child and skill in chronological order."""
    index = next(position for position, fact in enumerate(history) if fact.attempt_id == attempt_id)
    prior = history[max(0, index - WINDOW):index]
    following = history[index + 1:index + 1 + WINDOW]
    completed = True if session_state == "finished" else None
    if later_session_started:
        returned: bool | None = True
    elif now - session_started_at >= RETURN_OBSERVATION:
        returned = False
    else:
        returned = None
    return {"complete": len(following) == WINDOW, "prior_5": window_summary(prior), "next_5": window_summary(following), "session_completed": completed, "returned": returned}
