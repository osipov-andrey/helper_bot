import asyncio
import logging
import sys
from typing import BinaryIO

from aiogram import Bot, Dispatcher, F, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import BufferedInputFile, Message
from defaultenv import env

from inst_resizer.inst_resizer import get_triptych
from memento.events_consumer.rabbit_mq_consumer import (
    RabbitMQEventsConsumer,
    RabbitMQSettings,
)
from memento.facade.repository.sqlite_repository import SQLiteNotificationsRepo

TOKEN = env("BOT_TOKEN")

dp = Dispatcher()


class UnknownBotException(BaseException): ...


class MainMenu(StatesGroup):
    photo = State()


def _generate_main_menu() -> str:
    return "🖼️ /photo - crop photo for the instagram"


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """
    This handler receives messages with `/start` command
    """
    username = message.from_user.full_name if message.from_user else "Username"
    await message.answer(f"Hello, {html.bold(username)}!\n\nMain menu: \n{_generate_main_menu()}")


@dp.message(F.text.casefold() == "/photo")
async def command_photo_handler(message: Message, state: FSMContext) -> None:
    """
    This handler receives messages with `/photo` command
    """
    await state.set_state(MainMenu.photo)
    await message.answer("Send me photo to crop")


@dp.message(MainMenu.photo)
async def process_photo(message: Message, state: FSMContext) -> None:
    if not message.bot:
        raise UnknownBotException("There is no 'Bot' instance in the message!")
    if photos := message.photo:
        await message.answer("Nice")

        size = 3  # TODO: size selection
        photo = await message.bot.get_file(photos[size].file_id)
        if file_path := photo.file_path:
            photo_content: BinaryIO | None = await message.bot.download_file(file_path)
        else:
            raise UnknownBotException("There is no 'file_path' in the message!")
        if photo_content:
            for image_part in get_triptych(photo_content):
                file = BufferedInputFile(
                    image_part.getvalue(), filename=f"{photo.file_unique_id}_{image_part.name}.jpg"
                )
                await message.bot.send_photo(message.chat.id, file)
        else:
            await message.answer("There is no 'photo_content' in the message!")
    elif document := message.document:
        if document.mime_type != "image/jpeg":
            await message.answer("This document is not an image!")
            return
        await message.answer("Mmm, unzipped image! Very well!")
        if document_content := await message.bot.download(document.file_id):
            for image_part in get_triptych(document_content):
                file = BufferedInputFile(
                    image_part.getvalue(), filename=f"{document.file_unique_id}_{image_part.name}.jpg"
                )
                await message.bot.send_document(message.chat.id, file)
        else:
            await message.answer("There is no 'document_content' in the message!")
    else:
        await message.answer("This is not a photo!")
    await state.clear()


async def start_bot(bot: Bot) -> None:
    await dp.start_polling(bot)


async def main():
    # Initialize Bot instance with default bot properties which will be passed to all API calls
    bot_ = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    repo = SQLiteNotificationsRepo()
    consumer = RabbitMQEventsConsumer(bot_, repo, RabbitMQSettings())

    logging.basicConfig(level=logging.INFO, stream=sys.stdout)

    await asyncio.gather(start_bot(bot_), consumer.run())  # TODO: move consumer to an another process?


if __name__ == "__main__":
    asyncio.run(main())
