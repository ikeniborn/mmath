from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from mental_math.players.models import Player


async def owned_player(db: AsyncSession, account_id: UUID, player_id: UUID, *, lock: bool = False) -> Player:
    statement = select(Player).where(Player.id == player_id, Player.account_id == account_id)
    if lock:
        statement = statement.with_for_update()
    player = await db.scalar(statement)
    if player is None:
        raise HTTPException(404, detail={"code": "not_found"})
    return player
