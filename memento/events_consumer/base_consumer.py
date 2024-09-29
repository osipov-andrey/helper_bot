import abc
import logging
from typing import NoReturn

from aiogram import Bot

from memento.facade.repository.interface import NotificationsRepoInterface
from memento.notification import Notification


class BaseEventsConsumer(abc.ABC):

    def __init__(self, bot: Bot, repo: NotificationsRepoInterface):
        self._bot = bot
        self._repo = repo
        self._logger = logging.getLogger(__name__)

    @abc.abstractmethod
    async def run(self) -> NoReturn: ...

    async def send_notification(self, notification: Notification) -> Notification:
        try:
            await self._bot.send_message(notification.username, notification.text)
            notification.mark_as_reminded()
            await self._repo.update_notification(notification)
        except Exception as err:
            self._logger.error("Can't send message to %s", notification.username, exc_info=err)
        return notification
