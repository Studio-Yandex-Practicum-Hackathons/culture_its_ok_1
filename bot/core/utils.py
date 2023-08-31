import re
from asyncio import sleep
from datetime import datetime

from aiogram import types
from aiogram.fsm import context
from core.config import MEDIA_DIR, settings
from core.exceptions import LogicalError
import json
from pydub import AudioSegment
from vosk import Model, KaldiRecognizer
import soundfile as sf

EMAIL_REGEX = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
CHAT_ACTION_PERIOD = 3


async def reset_state(
        state: context.FSMContext,
        next_delay: int | None = None
):
    """Функция сбрасывает состояние state, кроме его значения next_delay,
    которое берётся либо из самого состояния, либо из переданной переменной
    next_delay."""
    state_data = await state.get_data()
    if next_delay is None:
        next_delay = state_data['next_delay'] if state_data.get('next_delay') else 0  # noqa: E501
    await state.clear()
    await state.set_data({'next_delay': next_delay})


async def delay_with_chat_action(
        message: types.Message,
        state: context.FSMContext,
        delay: int,
        chat_action: str
):
    """Т.к. отправка действия пользователю о том, что "бот печатает" или
    "бот отправляет фото" имеет срок действия около 5 секунд, функция спит
    delay секунд, но при этом обновляет отправленное действие каждые
    CHAT_ACTION_PERIOD секунд."""
    delays = [CHAT_ACTION_PERIOD] * (delay // CHAT_ACTION_PERIOD)
    if delay % CHAT_ACTION_PERIOD:
        delays.append(delay % CHAT_ACTION_PERIOD)

    for delay in delays:
        await message.bot.send_chat_action(chat_id=message.chat.id,
                                           action=chat_action)
        current_state = await state.get_state()
        await sleep(delay)
        if current_state != await state.get_state():
            # пользователь изменил состояние бота, прерываем отправку действия
            break


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

    current_state = await state.get_state()
    await delay_with_chat_action(message, state, state_data['next_delay'],
                                 'typing')
    if current_state != await state.get_state():
        # пользователь изменил состояние бота, прерываем отправку сообщения
        return message

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
    """Функция отправляет фотографию с предварительной задержкой, которая
    берётся из текущего состояния state. При этом, во время задержки
    пользователю отправляется уведомление, что бот загружает фото.
    Переменная next_delay отвечает за задержку перед показом следующего
    сообщения."""
    state_data = await state.get_data()

    current_state = await state.get_state()
    await delay_with_chat_action(message, state, state_data['next_delay'],
                                 'upload_photo')
    if current_state != await state.get_state():
        # пользователь изменил состояние бота, прерываем отправку фотографии
        return message

    if next_delay is None:
        next_delay = settings.bot.photo_show_delay + text_reading_time(caption)
    await state.update_data({'next_delay': next_delay})

    return await message.answer_photo(
        types.FSInputFile(MEDIA_DIR / photo_path),
        caption,
        **kwargs
    )


async def answer_poll_with_delay(
    message: types.Message,
    state: context.FSMContext,
    **kwargs
):
    """Функция отправляет квиз с предварительной задержкой, которая берётся
    из текущего состояния state. При этом, во время задержки пользователю
    отправляется уведомление, что бот печатает."""
    state_data = await state.get_data()

    current_state = await state.get_state()
    await delay_with_chat_action(message, state, state_data['next_delay'],
                                 'typing')
    if current_state != await state.get_state():
        # пользователь сбросил бота или перешёл в админку
        return message

    await state.update_data({'next_delay': 1})

    return await message.answer_poll(type='quiz', **kwargs)


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
        delay: int | None = None
):
    """Функция удаляет инлайн клавиатуру у полученного сообщения. Если
    установлена задержка delay, сделает это после задержки."""
    if delay:
        await sleep(delay)
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


def parse_quiz(content: str) -> dict:
    question, *answers = content.split('\n')
    options = []
    correct_option_id = None

    for i, answer in enumerate(answers):
        if not answer.strip():
            continue

        if answer.startswith('*'):
            if correct_option_id is not None:
                msg = 'В квизе не может быть больше одного ответа'
                raise LogicalError(msg)
            correct_option_id = i
            options.append(answer[1:].strip())
        else:
            options.append(answer.strip())

    if len(options) < 2:
        raise LogicalError('В квизе должно быть предложено хотя бы два ответа')

    if correct_option_id is None:
        raise LogicalError('В квизе не указан правильный ответ')

    return {
        'question': question,
        'options': options,
        'correct_option_id': correct_option_id
    }


def trim_audio(file_path: str, target_duration_s: int) -> None:
    """Функция обрезает файл голосового сообщения до заданной длины."""
    audio = AudioSegment.from_file(file_path)
    audio_duration_ms = len(audio)
    target_duration_ms = target_duration_s * 1000
    if audio_duration_ms > target_duration_ms:
        audio[:target_duration_ms].export(file_path, format="mp3")

        
def date_str_to_datetime(date: str, delimiter: str = '.'):
    """Преобразовывает дату в формате ДД.ММ.ГГГГ в datetime."""
    return datetime(*reversed(list(map(int, date.split(delimiter)))))


def calc_avg(values: list[int], n_digits: int) -> float:
    if not values:
        return 0
    return round(sum(values) / len(values), n_digits)

  
def speech_to_text(media):
    """Функция принимает путь к медиафайлу и возвращает текст."""
    FRAME_RATE = 16000
    CHANNELS = 1
    model = Model(r"core/vosk")
    rec = KaldiRecognizer(model, FRAME_RATE)
    rec.SetWords(True)
    # Используя библиотеку pydub и soundfile делаем предобработку аудио
    data, samplerate = sf.read(media)
    sf.write('temp.wav', data, samplerate)
    wav = AudioSegment.from_ogg("temp.wav")
    # Можно ограничить время аудио в примере первые 10 сек
    # wav = wav[:10000]
    wav = wav.set_channels(CHANNELS)
    wav = wav.set_frame_rate(FRAME_RATE)
    # Преобразуем вывод в json
    rec.AcceptWaveform(wav.raw_data)
    result = rec.Result()
    text = json.loads(result)["text"]
    return text
