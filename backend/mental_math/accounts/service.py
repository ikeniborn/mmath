from datetime import timedelta

from fastapi import HTTPException, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from mental_math.accounts.models import Account, AuthSession
from mental_math.accounts.security import CONFIRMATION_LIFETIME, digest, now


async def current_session(request: Request, db: AsyncSession) -> AuthSession | None:
    token = request.cookies.get("mmath_session")
    if not token:
        return None
    session = await db.get(AuthSession, digest(token))
    if session is None or session.revoked_at is not None or session.expires_at <= now():
        return None
    return session


async def require_account(request: Request, db: AsyncSession) -> Account:
    session = await current_session(request, db)
    if session is None:
        raise HTTPException(401, detail={"code": "session_expired"})
    account = await db.get(Account, session.account_id)
    if account is None:
        raise HTTPException(401, detail={"code": "session_expired"})
    return account


async def require_confirmation(request: Request, db: AsyncSession) -> Account:
    session = await current_session(request, db)
    if session is None:
        raise HTTPException(401, detail={"code": "session_expired"})
    if session.confirmed_at is None or session.confirmed_at + CONFIRMATION_LIFETIME <= now():
        raise HTTPException(403, detail={"code": "password_confirmation_required"})
    return await require_account(request, db)
