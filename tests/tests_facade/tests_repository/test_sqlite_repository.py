import os
from pathlib import Path

import pytest
from sqlalchemy.ext.asyncio import create_async_engine

from memento.facade.repository.interface import Notification
from memento.facade.repository.sqlite_repository.sqlite_repository import Base, SQLiteNotificationsRepo

TEST_DB_PATH = Path(__file__).parent.absolute().joinpath("db.sqlite")


@pytest.fixture
async def sqlite_engine():
    engine = create_async_engine(
        f"sqlite+aiosqlite:///{TEST_DB_PATH}",
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    try:
        yield engine
    finally:
        os.remove(TEST_DB_PATH)


@pytest.mark.asyncio
async def test_create_notification(sqlite_engine):
    notification = Notification(
        username="oscar.kokoshca",
        when="then",
        reminded=False,
        text="Wake up, samurai"
    )
    repo = SQLiteNotificationsRepo(TEST_DB_PATH)

    await repo.create_notification(notification)
    notifications = await repo.get_notifications()

    assert notifications[0] == notification
