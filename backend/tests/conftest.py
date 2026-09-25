import os
import subprocess
from dataclasses import dataclass, field
from uuid import UUID

import pytest
from httpx import ASGITransport, AsyncClient, Response
from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import create_async_engine

TEST_DATABASE_URL = "postgresql+psycopg://mmath_test:mmath_test@127.0.0.1:55434/mmath_t1_test"
os.environ["MMATH_DATABASE_URL"] = TEST_DATABASE_URL
os.environ["MMATH_ORIGIN"] = "http://test"
os.environ["MMATH_MODE"] = "lan-http"

from mental_math.main import create_app  # noqa: E402

TABLES = "policy_decisions, attempts, problems, learning_sessions, player_skills, players, auth_sessions, login_failures, accounts"
PASSWORD = "correct horse battery staple"


@pytest.fixture(scope="session", autouse=True)
def migrate_database():
    subprocess.run(["uv", "run", "--project", "backend", "alembic", "-c", "backend/alembic.ini", "upgrade", "head"], check=True, env=os.environ.copy())


@pytest.fixture(autouse=True)
async def clear_database(migrate_database):
    engine = create_async_engine(TEST_DATABASE_URL)
    async with engine.begin() as connection:
        await connection.execute(text(f"TRUNCATE TABLE {TABLES} CASCADE"))
    await engine.dispose()


@pytest.fixture
def app():
    return create_app()


@dataclass
class Family:
    client: AsyncClient
    parent_email: str
    player_id: str = ""
    csrf: str = ""

    def _headers(self) -> dict[str, str]:
        return {"X-CSRF-Token": self.csrf}

    async def get(self, path: str) -> Response:
        return await self.client.get(f"/api/v1{path}")

    async def post(self, path: str, json: dict | None = None) -> Response:
        return await self.client.post(f"/api/v1{path}", json=json, headers=self._headers())

    async def patch(self, path: str, json: dict) -> Response:
        return await self.client.patch(f"/api/v1{path}", json=json, headers=self._headers())


async def make_family(app, email: str, child: str) -> Family:
    client = AsyncClient(transport=ASGITransport(app=app), base_url="http://test", headers={"Origin": "http://test"})
    family = Family(client=client, parent_email=email)
    family.csrf = (await family.get("/auth/session")).json()["csrf_token"]
    registered = await family.post("/auth/register", {"email": email, "password": PASSWORD})
    assert registered.status_code == 201, registered.text
    family.csrf = registered.json()["csrf_token"]
    created = await family.post("/players", {"name": child, "age": 6, "topics": ["addition"]})
    assert created.status_code == 201, created.text
    family.player_id = created.json()["id"]
    return family


@pytest.fixture
async def family(app):
    result = await make_family(app, "family@example.com", "Masha")
    yield result
    await result.client.aclose()


@pytest.fixture
async def other_family(app):
    result = await make_family(app, "other@example.com", "Petya")
    yield result
    await result.client.aclose()


@dataclass
class Lesson:
    session_id: str
    problem: dict
    version: int
    command: dict = field(default_factory=dict)


@pytest.fixture
async def lesson(family) -> Lesson:
    started = await family.post("/sessions", {"player_id": family.player_id})
    assert started.status_code == 201, started.text
    snapshot = started.json()
    problem = snapshot["current_problem"]
    answer = problem["operand_a"] + problem["operand_b"]
    command = {"submission_id": "5f4b4b3e-9c3f-4c58-9e5e-1f7d5c1a0001", "problem_id": problem["id"], "answer": answer, "response_ms": 2500, "expected_version": snapshot["version"]}
    return Lesson(session_id=snapshot["id"], problem=problem, version=snapshot["version"], command=command)


@pytest.fixture
def counts(app):
    from mental_math.game.models import Attempt, LearningSession, PolicyDecision, Problem

    async def query(player_id: str) -> dict[str, int]:
        async with app.state.session_factory() as db:
            sessions = select(LearningSession.id).where(LearningSession.player_id == UUID(player_id))
            attempts = await db.scalar(select(func.count()).select_from(Attempt).where(Attempt.session_id.in_(sessions)))
            decisions = await db.scalar(select(func.count()).select_from(PolicyDecision).where(PolicyDecision.session_id.in_(sessions)))
            hinted_problems = await db.scalar(select(func.count()).select_from(Problem).where(Problem.session_id.in_(sessions), Problem.hinted_at.is_not(None)))
            hinted_attempts = await db.scalar(select(func.count()).select_from(Attempt).where(Attempt.session_id.in_(sessions), Attempt.hint_used.is_(True)))
            return {"attempts": attempts, "decisions": decisions, "hinted_problems": hinted_problems, "hinted_attempts": hinted_attempts}

    return query
