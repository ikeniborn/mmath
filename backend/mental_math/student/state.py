from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from mental_math.student.mastery import FORMULA_VERSION, WINDOW, summarize_window
from mental_math.student.models import PlayerSkill


async def get_or_create_skill(db: AsyncSession, player_id: UUID, skill: str, band: int, *, lock: bool = False) -> PlayerSkill:
    row = await db.get(PlayerSkill, (player_id, skill), with_for_update=lock)
    if row is None:
        row = PlayerSkill(player_id=player_id, skill=skill, band=band, attempts=0, correct=0, recent=[], correct_streak=0, error_streak=0)
        db.add(row)
        await db.flush()
    return row


async def record_attempt(db: AsyncSession, player_id: UUID, skill: str, band: int, *, correct: bool, hinted: bool, response_ms: int | None) -> PlayerSkill:
    """Update the child's independent skill aggregate inside the caller's transaction."""
    row = await get_or_create_skill(db, player_id, skill, band, lock=True)
    row.attempts += 1
    row.correct += int(correct)
    row.recent = (list(row.recent) + [{"correct": correct, "hinted": hinted, "response_ms": response_ms}])[-WINDOW:]
    # Promotion is earned per skill: the streak survives skill rotation and session boundaries.
    row.correct_streak = row.correct_streak + 1 if correct and not hinted else 0
    row.error_streak = 0 if correct else row.error_streak + 1
    summary = summarize_window(row.recent)
    row.mastery = summary.mastery if summary else None
    row.formula_version = FORMULA_VERSION
    return row
