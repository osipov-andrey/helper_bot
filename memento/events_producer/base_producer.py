import abc
import logging
from typing import NoReturn

from memento.facade.repository.interface import NotificationsRepoInterface


class BaseEventsProducer(abc.ABC):

    def __init__(self, repo: NotificationsRepoInterface):
        self._repo = repo
        self._logger = logging.getLogger(__name__)

    @abc.abstractmethod
    async def run(self) -> NoReturn: ...
