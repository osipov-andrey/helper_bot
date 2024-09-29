from typing import Any, Protocol

from memento.exceptions import MementoException
from memento.notification import Notification


class NotificationRepoException(MementoException): ...


class NotificationAlreadyExistsException(NotificationRepoException): ...


class NotificationNotFoundException(NotificationRepoException): ...


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

    async def delete_notification(self, **kwargs) -> None: ...
