import dataclasses
import uuid
from typing import Protocol

from memento.exceptions import MementoException


class NotificationRepoException(MementoException):
    ...


class NotificationAlreadyExistsException(NotificationRepoException):
    ...


class NotificationNotFoundException(NotificationRepoException):
    ...


@dataclasses.dataclass
class Notification:
    username: str
    when: str   # timestamp?
    reminded: bool = False
    text: str = ""
    id: str = dataclasses.field(default_factory=lambda: str(uuid.uuid4()))


class NotificationsRepoInterface(Protocol):

    async def create_notification(self, notification: Notification) -> None:
        """
        :raises NotificationAlreadyExistsException
        """
        ...

    async def update_notification(self, notification: Notification) -> None:
        """
        :raises NotificationNotFoundException
        """
        ...

    async def get_notifications(self) -> tuple[Notification, ...]:
        """
        :raises NotificationNotFoundException
        """
        ...

    async def delete_notification(self, **kwargs) -> None:
        ...
