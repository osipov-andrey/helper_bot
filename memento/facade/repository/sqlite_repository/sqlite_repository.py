from pathlib import Path
from typing import Any

from sqlalchemy import Boolean, Column, Integer, String, select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import (  # type: ignore  # mypy works bad with sqlalchemy
    declarative_base,
    sessionmaker,
)

from memento.facade.repository.interface import NotificationsRepoInterface
from memento.notification import Notification

SQLITE_PATH = Path(__file__).parent.absolute().joinpath("db.sqlite")
Base = declarative_base()


class _NotificationORM(Base):  # type: ignore  # mypy works bad with sqlalchemy
    __tablename__ = "notification"
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String)
    when = Column(String)
    reminded = Column(Boolean)
    text = Column(String)


class SQLiteNotificationsRepo(NotificationsRepoInterface):

    def __init__(self, db_path: Path = SQLITE_PATH):
        self.engine = create_async_engine(
            f"sqlite+aiosqlite:///{db_path}",
        )

    async def create_notification(self, notification: Notification) -> None:
        async_session = sessionmaker(self.engine, expire_on_commit=False, class_=AsyncSession)
        async with async_session() as session:
            async with session.begin():
                session.add_all(
                    [
                        _NotificationORM(
                            username=notification.username,
                            when=notification.when,
                            reminded=notification.reminded,
                            text=notification.text,
                        ),
                    ]
                )
        await session.commit()

    async def get_notifications(self, **kwargs: Any) -> tuple[Notification, ...]:
        _select = select(_NotificationORM).order_by(_NotificationORM.id)
        if kwargs.get("reminded") is False:
            _select = _select.where(_NotificationORM.reminded is False)

        async_session = sessionmaker(self.engine, expire_on_commit=False, class_=AsyncSession)
        async with async_session() as session:
            async with session.begin():
                result = await session.execute(_select)  # TODO: options
                return tuple(
                    (
                        Notification(id=n.id, username=n.username, when=n.when, reminded=n.reminded, text=n.text)
                        for n in result.scalars()
                    )
                )
