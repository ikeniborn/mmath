from uuid import UUID

from fastapi import APIRouter, Depends, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from mental_math.accounts.routes import ensure_csrf
from mental_math.accounts.service import current_session, require_account, require_confirmation
from mental_math.db import get_db
from mental_math.players.models import Player
from mental_math.players.schemas import PlayerInput, PlayerPatch, PlayerView
from mental_math.players.service import owned_player

router = APIRouter(prefix="/api/v1/players", tags=["players"])


def view(player: Player) -> dict:
    return {"id": player.id, "name": player.name, "age": player.age, "avatar": player.avatar, "topics": player.topics, "mode": player.mode, "difficulty_band": player.difficulty_band, "session_minutes": player.session_minutes}


@router.get("", response_model=list[PlayerView])
async def list_players(request: Request, db: AsyncSession = Depends(get_db, scope="function")):
    account = await require_account(request, db)
    players = (await db.scalars(select(Player).where(Player.account_id == account.id).order_by(Player.name))).all()
    return [view(player) for player in players]


@router.post("", status_code=201, response_model=PlayerView)
async def create_player(body: PlayerInput, request: Request, db: AsyncSession = Depends(get_db, scope="function")):
    account = await require_account(request, db)
    session = await current_session(request, db)
    ensure_csrf(request, session)
    player = Player(account_id=account.id, **body.model_dump())
    db.add(player)
    await db.flush()
    return view(player)


@router.get("/{player_id}", response_model=PlayerView)
async def get_player(player_id: UUID, request: Request, db: AsyncSession = Depends(get_db, scope="function")):
    account = await require_account(request, db)
    return view(await owned_player(db, account.id, player_id))


@router.patch("/{player_id}", response_model=PlayerView)
async def update_player(player_id: UUID, body: PlayerPatch, request: Request, db: AsyncSession = Depends(get_db, scope="function")):
    session = await current_session(request, db)
    ensure_csrf(request, session)
    account = await require_confirmation(request, db)
    player = await owned_player(db, account.id, player_id, lock=True)
    for key, value in body.model_dump(exclude_unset=True).items():
        setattr(player, key, value)
    return view(player)
