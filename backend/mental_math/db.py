from collections.abc import AsyncIterator
from fastapi import HTTPException, Request
from sqlalchemy.exc import IntegrityError

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


def session_factory(database_url: str) -> async_sessionmaker[AsyncSession]:
    engine = create_async_engine(database_url, pool_pre_ping=True)
    return async_sessionmaker(engine, expire_on_commit=False)


async def get_db(request: Request) -> AsyncIterator[AsyncSession]:
    async with request.app.state.session_factory() as db:
        try:
            yield db
            await db.commit()
        except IntegrityError as error:
            await db.rollback()
            raise HTTPException(409, detail={"code": "conflict"}) from error
        except Exception:
            await db.rollback()
            raise
