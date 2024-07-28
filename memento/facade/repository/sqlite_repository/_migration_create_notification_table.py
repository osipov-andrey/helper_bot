import asyncio

from sqlalchemy.ext.asyncio import create_async_engine

from memento.facade.repository.sqlite_repository.sqlite_repository import (
    SQLITE_PATH,
    Base,
)


async def up():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def down():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


if __name__ == "__main__":
    engine = create_async_engine(
        f"sqlite+aiosqlite:///{SQLITE_PATH}",
    )
    asyncio.run(up())
