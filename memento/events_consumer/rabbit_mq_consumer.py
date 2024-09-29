import dataclasses
import json
from typing import NoReturn

import aio_pika
from aio_pika.connection import make_url
from aiogram import Bot

from memento.events_consumer.base_consumer import BaseEventsConsumer
from memento.facade.repository.interface import NotificationsRepoInterface
from memento.notification import Notification

DEFAULT_QUEUE_NAME = "notifications-ready-for-delivery"


@dataclasses.dataclass(frozen=True, slots=True)
class RabbitMQSettings:
    host: str = "localhost"
    port: int = 5672
    login: str = "guest"
    password: str = "guest"
    virtualhost: str = "/"
    queue_name: str = DEFAULT_QUEUE_NAME


class RabbitMQEventsConsumer(BaseEventsConsumer):

    def __init__(self, bot: Bot, repo: NotificationsRepoInterface, settings: RabbitMQSettings):
        super().__init__(bot, repo)
        self._settings = settings
        self._amqp_uri = make_url(
            host=settings.host,
            port=settings.port,
            login=settings.login,
            password=settings.password,
            virtualhost=settings.virtualhost,
        )

    async def run(self) -> NoReturn:
        connection = await aio_pika.connect_robust(self._amqp_uri)
        async with connection:
            channel = await connection.channel()
            await channel.set_qos(prefetch_count=10)
            queue = await channel.declare_queue(self._settings.queue_name)

            async with queue.iterator() as queue_iter:
                async for message in queue_iter:
                    try:
                        await self._on_message(message.body.decode())
                    except Exception:
                        raise
                    else:
                        await message.ack()
        raise RuntimeError("Consumer stooped!")

    async def _on_message(self, message: str) -> None:
        try:
            notification = Notification(**json.loads(message))
        except TypeError as err:
            self._logger.warning("Unsupported message format: ", exc_info=err)
            return None
        await self.send_notification(notification)
        if not notification.reminded:
            # TODO: back to Queue
            pass
