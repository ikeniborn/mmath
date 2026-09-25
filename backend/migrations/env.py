import asyncio
import os

from alembic import context
from sqlalchemy.ext.asyncio import async_engine_from_config
from sqlalchemy import pool

from mental_math.db import Base
from mental_math.accounts import models as account_models  # noqa: F401
from mental_math.players import models as player_models  # noqa: F401
from mental_math.game import models as game_models  # noqa: F401
from mental_math.student import models as student_models  # noqa: F401

config = context.config
database_url = os.environ.get("MMATH_DATABASE_URL")
if not database_url:
    raise RuntimeError("MMATH_DATABASE_URL is required")
config.set_main_option("sqlalchemy.url", database_url)


def run_migrations_offline():
    context.configure(url=database_url, target_metadata=Base.metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    context.configure(connection=connection, target_metadata=Base.metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online():
    engine = async_engine_from_config(config.get_section(config.config_ini_section), prefix="sqlalchemy.", poolclass=pool.NullPool)
    async with engine.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await engine.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
