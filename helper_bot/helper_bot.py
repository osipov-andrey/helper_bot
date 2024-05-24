import asyncio
import io
import logging
import sys

from aiogram import Bot, Dispatcher, F, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import BufferedInputFile, Message
from defaultenv import env

from inst_resizer.inst_resizer import get_triptych

TOKEN = env("BOT_TOKEN")

dp = Dispatcher()


class MainMenu(StatesGroup):
    photo = State()


def _generate_main_menu() -> str:
    return "🖼️ /photo - crop photo for the instagram"


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """
    This handler receives messages with `/start` command
    """
    await message.answer(f"Hello, {html.bold(message.from_user.full_name)}!\n\nMain menu: \n{_generate_main_menu()}")


@dp.message(F.text.casefold() == "/photo")
async def command_photo_handler(message: Message, state: FSMContext) -> None:
    """
    This handler receives messages with `/photo` command
    """
    await state.set_state(MainMenu.photo)
    await message.answer("Send me photo to crop")


@dp.message(MainMenu.photo)
async def process_photo(message: Message, state: FSMContext) -> None:
    if photos := message.photo:  # TODO: uncompressed files support
        await message.answer("Nice")

        size = 3  # TODO: size selection
        photo = await message.bot.get_file(photos[size].file_id)
        file_path = photo.file_path
        photo_content: io.BytesIO | None = await message.bot.download_file(file_path)

        for image_part in get_triptych(photo_content):
            file = BufferedInputFile(image_part.getvalue(), filename=f"{photo.file_unique_id}_{image_part.name}.jpg")
            await message.bot.send_photo(message.chat.id, file)

    else:
        await message.answer("This is not a photo!")
        await state.clear()


async def main() -> None:
    # Initialize Bot instance with default bot properties which will be passed to all API calls
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    # And the run events dispatching
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
