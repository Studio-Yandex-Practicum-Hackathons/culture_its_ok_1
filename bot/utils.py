from asyncio import sleep

from aiogram import Bot, types
from core.config import MEDIA_DIR
from core.config import settings


bot = Bot(token=settings.bot.telegram_token)


async def send_message_and_sleep(
    message: types.Message,
    text: str,
    delay: int = 1,
    **kwargs
):
    await bot.send_chat_action(chat_id=message.chat.id, action='typing')
    await sleep(delay)
    await message.answer(text, **kwargs)
    await sleep(delay)


async def send_photo_and_sleep(
    message: types.Message,
    photo_path: str,
    delay: int = 5,
    **kwargs
):
    await bot.send_chat_action(chat_id=message.chat.id, action='upload_photo')
    await sleep(delay)
    await message.answer_photo(
        types.FSInputFile(MEDIA_DIR / photo_path), **kwargs)
    await sleep(delay)
