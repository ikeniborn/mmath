import secrets
from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.responses import JSONResponse
from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from mental_math.accounts.models import Account, AuthSession, LoginFailure
from mental_math.accounts.schemas import Credentials, PasswordConfirmation, SessionView
from mental_math.accounts.security import SESSION_LIFETIME, digest, hasher, now, random_token, verify_password
from mental_math.accounts.service import current_session, require_account
from mental_math.db import get_db

router = APIRouter(prefix="/api/v1/auth", tags=["accounts"])


def ensure_csrf(request: Request, session: AuthSession | None = None) -> None:
    origin = request.headers.get("origin")
    if origin != request.app.state.settings.origin:
        raise HTTPException(403, detail={"code": "invalid_origin"})
    supplied = request.headers.get("x-csrf-token", "")
    expected = session.csrf_hash if session else digest(request.cookies.get("mmath_preauth", ""))
    if not supplied or not secrets.compare_digest(digest(supplied), expected):
        raise HTTPException(403, detail={"code": "invalid_csrf"})


def session_cookie(response: Response, token: str, request: Request) -> None:
    response.set_cookie("mmath_session", token, max_age=int(SESSION_LIFETIME.total_seconds()), secure=request.app.state.settings.mode == "public", httponly=True, samesite="lax", path="/")


async def issue_session(db: AsyncSession, account: Account, response: Response, request: Request) -> str:
    token, csrf = random_token(), random_token()
    db.add(AuthSession(token_hash=digest(token), csrf_hash=digest(csrf), account_id=account.id, expires_at=now() + SESSION_LIFETIME))
    session_cookie(response, token, request)
    return csrf


@router.get("/session", response_model=SessionView)
async def session_info(request: Request, response: Response, db: AsyncSession = Depends(get_db, scope="function")):
    session = await current_session(request, db)
    if session:
        account = await db.get(Account, session.account_id)
        csrf = request.cookies.get("mmath_auth_csrf")
        if csrf and secrets.compare_digest(digest(csrf), session.csrf_hash):
            return {"email": account.email, "csrf_token": csrf}
    csrf = request.cookies.get("mmath_preauth")
    if not csrf:
        csrf = random_token()
        response.set_cookie("mmath_preauth", csrf, secure=request.app.state.settings.mode == "public", httponly=True, samesite="lax", path="/")
    return {"email": None, "csrf_token": csrf}


@router.post("/register", status_code=201, response_model=SessionView)
async def register(body: Credentials, request: Request, response: Response, db: AsyncSession = Depends(get_db, scope="function")):
    ensure_csrf(request)
    email = str(body.email).lower()
    if await db.scalar(select(Account.id).where(Account.email == email)):
        raise HTTPException(409, detail={"code": "email_unavailable"})
    account = Account(email=email, password_hash=hasher.hash(body.password))
    db.add(account)
    await db.flush()
    csrf = await issue_session(db, account, response, request)
    response.set_cookie("mmath_auth_csrf", csrf, secure=request.app.state.settings.mode == "public", httponly=True, samesite="lax", path="/")
    return {"email": email, "csrf_token": csrf}


@router.post("/login", response_model=SessionView)
async def login(body: Credentials, request: Request, response: Response, db: AsyncSession = Depends(get_db, scope="function")):
    ensure_csrf(request)
    email = str(body.email).lower()
    ip = request.client.host if request.client else "unknown"
    cutoff = now() - timedelta(minutes=15)
    failures = await db.scalar(select(func.count()).select_from(LoginFailure).where(LoginFailure.email == email, LoginFailure.ip_address == ip, LoginFailure.occurred_at > cutoff))
    if failures >= 5:
        raise HTTPException(429, detail={"code": "login_throttled"})
    account = await db.scalar(select(Account).where(Account.email == email))
    if account is None or not verify_password(account.password_hash, body.password):
        db.add(LoginFailure(email=email, ip_address=ip))
        return JSONResponse({"detail": {"code": "invalid_credentials"}}, status_code=401)
    await db.execute(delete(LoginFailure).where(LoginFailure.email == email, LoginFailure.ip_address == ip))
    old = await current_session(request, db)
    if old:
        old.revoked_at = now()
    csrf = await issue_session(db, account, response, request)
    response.set_cookie("mmath_auth_csrf", csrf, secure=request.app.state.settings.mode == "public", httponly=True, samesite="lax", path="/")
    return {"email": email, "csrf_token": csrf}


@router.post("/logout", status_code=204)
async def logout(request: Request, response: Response, db: AsyncSession = Depends(get_db, scope="function")):
    session = await current_session(request, db)
    if not session:
        raise HTTPException(401, detail={"code": "session_expired"})
    ensure_csrf(request, session)
    session.revoked_at = now()
    response.delete_cookie("mmath_session", path="/")
    response.delete_cookie("mmath_auth_csrf", path="/")


@router.post("/confirm-password", status_code=204)
async def confirm_password(body: PasswordConfirmation, request: Request, db: AsyncSession = Depends(get_db, scope="function")):
    session = await current_session(request, db)
    if not session:
        raise HTTPException(401, detail={"code": "session_expired"})
    ensure_csrf(request, session)
    account = await require_account(request, db)
    if not verify_password(account.password_hash, body.password):
        raise HTTPException(403, detail={"code": "invalid_password"})
    session.confirmed_at = now()
