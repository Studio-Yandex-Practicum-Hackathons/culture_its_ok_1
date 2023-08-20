from asyncio import sleep

from aiogram import types


async def send_message_and_sleep(
    message: types.Message,
    text: str,
    delay: int = 1,
    **kwargs
):
    await message.answer(text, **kwargs)
    await sleep(delay)
