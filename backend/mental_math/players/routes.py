from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from mental_math.accounts.routes import ensure_csrf
from mental_math.accounts.service import current_session, require_account, require_confirmation
from mental_math.db import get_db
from mental_math.game.catalogue import eligible_pairs, supported_bands
from mental_math.game.models import LearningSession
from mental_math.players.models import Player
from mental_math.players.schemas import PlayerInput, PlayerPatch, PlayerView, ProgressView
from mental_math.players.service import owned_player
from mental_math.student.models import PlayerSkill

router = APIRouter(prefix="/api/v1/players", tags=["players"])


def view(player: Player) -> dict:
    return {"id": player.id, "name": player.name, "age": player.age, "avatar": player.avatar, "topics": player.topics, "mode": player.mode, "difficulty_band": player.difficulty_band, "session_minutes": player.session_minutes, "theme": player.theme}


def ensure_supported(topics: list[str], mode: str, band: int) -> None:
    """Fixed mode must lock a band that at least one enabled skill supports; otherwise name the alternatives."""
    if mode == "fixed" and not eligible_pairs(topics, mode, band):
        raise HTTPException(422, detail={"code": "unsupported_difficulty", "supported_bands": supported_bands(topics)})


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
    ensure_supported(body.topics, body.mode, body.difficulty_band)
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
    merged = {**view(player), **body.model_dump(exclude_unset=True)}
    ensure_supported(merged["topics"], merged["mode"], merged["difficulty_band"])
    for key, value in body.model_dump(exclude_unset=True).items():
        setattr(player, key, value)
    return view(player)


@router.get("/{player_id}/progress", response_model=ProgressView)
async def progress(player_id: UUID, request: Request, limit: int = Query(default=20, ge=1, le=100), offset: int = Query(default=0, ge=0), db: AsyncSession = Depends(get_db, scope="function")):
    account = await require_account(request, db)
    player = await owned_player(db, account.id, player_id)
    skills = (await db.scalars(select(PlayerSkill).where(PlayerSkill.player_id == player.id).order_by(PlayerSkill.skill))).all()
    total = await db.scalar(select(func.count()).select_from(LearningSession).where(LearningSession.player_id == player.id))
    sessions = (await db.scalars(select(LearningSession).where(LearningSession.player_id == player.id).order_by(LearningSession.started_at.desc(), LearningSession.id.desc()).limit(limit).offset(offset))).all()
    return {
        "skills": [{"skill": row.skill, "band": row.band, "attempts": row.attempts, "correct": row.correct, "mastery": row.mastery, "formula_version": row.formula_version, "updated_at": row.updated_at} for row in skills],
        "sessions": [{"id": row.id, "state": row.state, "started_at": row.started_at, "finished_at": row.finished_at, "answered_count": row.answered_count, "correct_count": row.correct_count, "active_ms": row.active_ms, "settings": row.settings} for row in sessions],
        "total_sessions": total,
    }
