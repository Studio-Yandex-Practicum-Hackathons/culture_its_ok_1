import re
from asyncio import sleep

from aiogram import types
from aiogram.fsm import context
from pydub import AudioSegment

from core.config import MEDIA_DIR, settings

EMAIL_REGEX = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
CHAT_ACTION_PERIOD = 5


async def reset_state(
        state: context.FSMContext,
        next_delay: int | None = None
):
    """Функция сбрасывает состояние state, кроме его значения next_delay,
    которое берётся либо из самого состояния, либо из переданной переменной
    next_delay."""
    state_data = await state.get_data()
    if next_delay is None:
        next_delay = state_data['next_delay']
    await state.clear()
    await state.set_data({'next_delay': next_delay})


async def delay_with_chat_action(
        message: types.Message,
        delay: int,
        chat_action: str
):
    """Т.к. отправка действия пользователю о том, что "бот печатает" или
    "бот загружает фото" имеет срок действия около 5 секунд, функция спит delay
    секунд, но при этом обновляет отправленное действие каждые 5 секунд"""
    delays = [CHAT_ACTION_PERIOD] * (delay // CHAT_ACTION_PERIOD)
    if delay % CHAT_ACTION_PERIOD:
        delays.append(delay % CHAT_ACTION_PERIOD)

    for delay in delays:
        await message.bot.send_chat_action(chat_id=message.chat.id,
                                           action=chat_action)
        await sleep(delay)


async def answer_with_delay(
    message: types.Message,
    state: context.FSMContext,
    text: str,
    next_delay: int | None = None,
    **kwargs
):
    """Функция отправляет текст с предварительной задержкой, равной времени
    прочтения текста/просмотра фотографии пользователем, отправленных
    в предыдущем сообщении. При этом, во время задержки пользователю
    отправляется уведомление, что бот печатает. Переменная next_delay отвечает
    за задержку перед показом следующего сообщения."""
    state_data = await state.get_data()
    await delay_with_chat_action(message, state_data['next_delay'], 'typing')

    if next_delay is None:
        next_delay = text_reading_time(text)
    await state.update_data({'next_delay': next_delay})

    return await message.answer(text, **kwargs)


async def answer_photo_with_delay(
    message: types.Message,
    state: context.FSMContext,
    photo_path: str,
    caption: str | None = None,
    next_delay: int | None = None,
    **kwargs
):
    """Функция отправляет фотографию с предварительной задержкой, равной
    времени прочтения текста/просмотра фотографии пользователем, отправленных
    в предыдущем сообщении. При этом, во время задержки пользователю
    отправляется уведомление, что бот загружает фото. Переменная next_delay
    отвечает за задержку перед показом следующего сообщения."""
    state_data = await state.get_data()
    await delay_with_chat_action(message, state_data['next_delay'],
                                 'upload_photo')

    if next_delay is None:
        next_delay = settings.bot.photo_show_delay + text_reading_time(caption)
    await state.update_data({'next_delay': next_delay})

    return await message.answer_photo(
        types.FSInputFile(MEDIA_DIR / photo_path),
        caption,
        **kwargs
    )


async def send_message_and_sleep(
    message: types.Message,
    text: str,
    delay: int = 1,
    **kwargs
):
    """Функция отправляет сообщение и засыпает на delay секунд."""
    result = await message.answer(text, **kwargs)
    await sleep(delay)
    return result  # noqa: R504


async def delete_keyboard(
        message: types.Message,
):
    """Функция удаляет обычную клавиатуру. Телеграм не позволяет удалять такую
    клавиатуру без отправки сообщения пользователю, поэтому после отправки
    сообщение-пустышка сразу удаляется."""
    msg = await message.answer('...', reply_markup=types.ReplyKeyboardRemove())
    await msg.delete()


async def delete_inline_keyboard(
        message: types.Message,
):
    """Функция удаляет инлайн клавиатуру у полученного сообщения."""
    await message.edit_reply_markup(reply_markup=None)


def text_reading_time(
        text: str | None,
        words_per_minute: int = settings.bot.reading_speed
) -> int:
    """
    Функция возвращает время в секундах, необходимое для прочтения текста text
    человеком со скоростью words_per_minute (слов в минуту). Минимальное время
    чтения текста любого размера - 1 секунда"""
    if text is None:
        return 0
    return max(1, int(len(text.split()) / words_per_minute * 60))


def check_is_email(email: str) -> bool:
    """Функция проверяет, является ли email валидным адресом электронной
    почты."""
    return bool(re.fullmatch(EMAIL_REGEX, email))


def trim_audio(input_path, output_path, target_duration):
    # Загрузка аудиофайла
    audio = AudioSegment.from_mp3(input_path)

    # Определение длительности аудиофайла в миллисекундах
    audio_duration = len(audio)

    # Определение длительности обрезанного аудио в миллисекундах
    target_duration_ms = target_duration * 1000

    if audio_duration <= target_duration_ms:
        # Если аудио уже короче или равно желаемой длительности,
        # сохраняем его как есть
        audio.export(output_path, format="mp3")
    else:
        # Обрезаем аудио до заданной длительности
        trimmed_audio = audio[:target_duration_ms]
        trimmed_audio.export(output_path, format="mp3")

# Пример использования функции
input_audio_path = "input_audio.mp3"  # Путь к исходному аудиофайлу
output_audio_path = "output_audio.mp3"  # Путь для сохранения обрезанного аудиофайла
target_duration = 30  # Желаемая длительность аудио в секундах

# trim_audio(input_audio_path, output_audio_path, target_duration)