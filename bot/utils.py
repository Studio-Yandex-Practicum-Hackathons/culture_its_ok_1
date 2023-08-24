from asyncio import sleep

from aiogram import types
from core.config import MEDIA_DIR


async def send_message_and_sleep(
    message: types.Message,
    text: str,
    delay: int | None = None,
    **kwargs
):
    if delay is None:
        # TODO: установить автоматическую задержку
        delay = 0
    result = await message.answer(text, **kwargs)
    await sleep(delay)
    return result  # noqa: R504


async def send_photo_and_sleep(
    message: types.Message,
    photo_path: str,
    delay: int = 0,
    **kwargs
):
    result = await message.answer_photo(
        types.FSInputFile(MEDIA_DIR / photo_path),
        **kwargs
    )
    await sleep(delay)
    return result  # noqa: R504


async def delete_keyboard(
        message: types.Message,
):
    msg = await message.answer('...', reply_markup=types.ReplyKeyboardRemove())
    await msg.delete()


async def delete_inline_keyboard(
        message: types.Message,
):
    await message.edit_reply_markup(reply_markup=None)
