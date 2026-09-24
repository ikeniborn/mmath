import os
import subprocess

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine


TEST_DATABASE_URL = "postgresql+psycopg://mmath_test:mmath_test@127.0.0.1:55434/mmath_t1_test"
os.environ["MMATH_DATABASE_URL"] = TEST_DATABASE_URL
os.environ["MMATH_ORIGIN"] = "http://test"
os.environ["MMATH_MODE"] = "lan-http"


@pytest.fixture(scope="session", autouse=True)
def migrate_database():
    subprocess.run(["uv", "run", "--project", "backend", "alembic", "-c", "backend/alembic.ini", "upgrade", "head"], check=True, env=os.environ.copy())


@pytest.fixture(autouse=True)
async def clear_database(migrate_database):
    engine = create_async_engine(TEST_DATABASE_URL)
    async with engine.begin() as connection:
        await connection.execute(text("TRUNCATE TABLE players, auth_sessions, login_failures, accounts CASCADE"))
    await engine.dispose()
