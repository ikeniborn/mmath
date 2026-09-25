from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from mental_math.student.models import PlayerSkill


async def record_attempt(db: AsyncSession, player_id: UUID, skill: str, band: int, correct: bool) -> PlayerSkill:
    """Update the child's independent skill aggregate inside the caller's transaction."""
    row = await db.get(PlayerSkill, (player_id, skill), with_for_update=True)
    if row is None:
        row = PlayerSkill(player_id=player_id, skill=skill, band=band, attempts=0, correct=0)
        db.add(row)
    row.attempts += 1
    row.correct += int(correct)
    return row
