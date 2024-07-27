import dataclasses
from typing import Protocol, Any

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
    id: str | None = None

    def __eq__(self, other: 'Notification') -> bool:
        self_dict = dataclasses.asdict(self)
        self_dict.pop("id")
        other_dict = dataclasses.asdict(other)
        other_dict.pop("id")
        return self_dict == other_dict


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

    async def get_notifications(self, **kwargs: Any) -> tuple[Notification, ...]:
        """
        :raises NotificationNotFoundException
        """
        ...

    async def delete_notification(self, **kwargs) -> None:
        ...
