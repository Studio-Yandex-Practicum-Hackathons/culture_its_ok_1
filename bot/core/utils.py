import re
from asyncio import sleep

from aiogram import types
from core.config import MEDIA_DIR, settings

EMAIL_REGEX = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'


async def send_message_and_sleep(
    message: types.Message,
    text: str,
    delay: int | None = None,
    **kwargs
):
    """Функция отправляет сообщение и засыпает на delay секунд. Если delay
    не установлен, функция засыпает время, необходимое для прочтения сообщения
    со скоростью, которая установлена в настройках бота."""
    if delay is None:
        delay = text_reading_time(text)
    result = await message.answer(text, **kwargs)
    await sleep(delay)
    return result  # noqa: R504


async def send_photo_and_sleep(
    message: types.Message,
    photo_path: str,
    delay: int | None = None,
    **kwargs
):
    """Функция отправляет фотографию и засыпает на delay секунд. Если delay
    не установлен, функция засыпает на то время, которое установлено в
    настройках бота."""
    if delay is None:
        delay = settings.bot.photo_showing_delay

    result = await message.answer_photo(
        types.FSInputFile(MEDIA_DIR / photo_path),
        **kwargs
    )
    await sleep(delay)
    return result  # noqa: R504


async def delete_keyboard(
        message: types.Message,
):
    """Функция удаляет обычную клавиатуру. Телеграм не позволяет удалять такую
    клавиатуру без отправки сообщения пользователю, поэтому, после отправки
    сообщение-пустышка сразу удаляется."""
    msg = await message.answer('...', reply_markup=types.ReplyKeyboardRemove())
    await msg.delete()


async def delete_inline_keyboard(
        message: types.Message,
):
    """Функция удаляет инлайн клавиатуру у полученного сообщения."""
    await message.edit_reply_markup(reply_markup=None)


def text_reading_time(
        text: str,
        words_per_minute: int = settings.bot.words_per_minute
) -> int:
    """
    Функция возвращает время в секундах, необходимое для прочтения текста
    пользователем.
    :param text: Читаемый текст
    :param words_per_minute: Скорость чтения (слов в минуту)
    :return: Время чтения в секундах
    """
    return max(1, int(len(text.split()) / words_per_minute * 60))


def check_is_email(email: str) -> bool:
    return bool(re.fullmatch(EMAIL_REGEX, email))
