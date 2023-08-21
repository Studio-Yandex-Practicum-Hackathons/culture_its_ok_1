from asyncio import sleep

from aiogram import types
from core.config import MEDIA_DIR


async def send_message_and_sleep(
    message: types.Message,
    text: str,
    delay: int = 0,
    **kwargs
):
    await message.answer(text, **kwargs)
    await sleep(delay)


async def send_photo_and_sleep(
    message: types.Message,
    photo_path: str,
    delay: int = 0,
    **kwargs
):
    await message.answer_photo(
        types.FSInputFile(MEDIA_DIR / photo_path),
        **kwargs
    )
    await sleep(delay)


async def delete_keyboard(
        message: types.Message,
):
    msg = await message.answer('...', reply_markup=types.ReplyKeyboardRemove())
    await msg.delete()
