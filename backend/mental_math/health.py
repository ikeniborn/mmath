"""Liveness and readiness. Readiness checks the database and the Alembic schema, never the Framework."""

from pathlib import Path

from alembic.config import Config
from alembic.script import ScriptDirectory
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from sqlalchemy import text

router = APIRouter(tags=["health"])
_ALEMBIC_INI = Path(__file__).resolve().parents[1] / "alembic.ini"


def expected_revision() -> str:
    return ScriptDirectory.from_config(Config(str(_ALEMBIC_INI))).get_current_head()


@router.get("/health/live")
async def live():
    return {"status": "live"}


@router.get("/health/ready")
async def ready(request: Request):
    database, schema = "unavailable", "unknown"
    try:
        async with request.app.state.session_factory() as db:
            current = await db.scalar(text("SELECT version_num FROM alembic_version"))
            database = "ok"
            schema = "ok" if current == expected_revision() else "mismatch"
    except Exception:  # noqa: BLE001 - the reason stays in server logs, never in the response
        request.app.state.logger.warning("readiness database check failed", extra={"check": "database"})
    status = "ready" if database == "ok" and schema == "ok" else "not_ready"
    return JSONResponse({"status": status, "database": database, "schema": schema}, status_code=200 if status == "ready" else 503)
