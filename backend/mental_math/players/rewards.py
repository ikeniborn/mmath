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
