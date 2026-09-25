from uuid import UUID

from fastapi import APIRouter, Depends, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession

from mental_math.accounts.routes import ensure_csrf
from mental_math.accounts.service import current_session, require_account
from mental_math.db import get_db
from mental_math.game import engine
from mental_math.game.schemas import AdvanceSession, AttemptResult, SessionSnapshot, StartSession, SubmitAttempt

router = APIRouter(prefix="/api/v1/sessions", tags=["game"])


async def _mutating_account(request: Request, db: AsyncSession):
    session = await current_session(request, db)
    account = await require_account(request, db)
    ensure_csrf(request, session)
    return account


@router.post("", response_model=SessionSnapshot, responses={201: {"model": SessionSnapshot}})
async def start_session(body: StartSession, request: Request, response: Response, db: AsyncSession = Depends(get_db, scope="function")):
    account = await _mutating_account(request, db)
    result, created = await engine.start_session(db, account.id, body.player_id)
    response.status_code = 201 if created else 200
    return result


@router.get("/{session_id}", response_model=SessionSnapshot)
async def read_session(session_id: UUID, request: Request, db: AsyncSession = Depends(get_db, scope="function")):
    account = await require_account(request, db)
    return await engine.read_session(db, account.id, session_id)


@router.post("/{session_id}/attempts", response_model=AttemptResult)
async def submit_attempt(session_id: UUID, body: SubmitAttempt, request: Request, db: AsyncSession = Depends(get_db, scope="function")):
    account = await _mutating_account(request, db)
    return await engine.submit_attempt(db, account.id, session_id, body)


@router.post("/{session_id}/advance", response_model=SessionSnapshot)
async def advance_session(session_id: UUID, body: AdvanceSession, request: Request, db: AsyncSession = Depends(get_db, scope="function")):
    account = await _mutating_account(request, db)
    return await engine.advance_session(db, account.id, session_id, body.attempt_id, body.expected_version)


@router.post("/{session_id}/finish", response_model=SessionSnapshot)
async def finish_session(session_id: UUID, request: Request, db: AsyncSession = Depends(get_db, scope="function")):
    account = await _mutating_account(request, db)
    return await engine.finish_session(db, account.id, session_id)
