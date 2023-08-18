from aiogram import Router, types, F
from core.logger import log_dec, logger_factory
from aiogram.fsm import context
from states import NewUser, Route
import re
from dummy_db import USERS
from utils import send_message_and_sleep

router = Router()
logger = logger_factory(__name__)

MIN_NAME_LENGTH = 2
MAX_NAME_LENGTH = 30

MIN_AGE = 2
MAX_AGE = 125


@router.message(NewUser.name_input, F.text)
@log_dec(logger)
async def name_input(message: types.Message, state: context.FSMContext):
    pattern = rf'^\D{{{MIN_NAME_LENGTH},{MAX_NAME_LENGTH}}}$'
    if not re.match(pattern, message.text):
        await message.answer('Пожалуйста, введите ваше настоящее имя.')
        return

    await state.set_data(dict(name=message.text))

    await message.answer('Пожалуйста, введите ваш возраст.')
    await state.set_state(NewUser.age_input)


@router.message(NewUser.age_input, F.text)
@log_dec(logger)
async def name_input(message: types.Message, state: context.FSMContext):
    if (
        not message.text.isdecimal() or
        message.text.isdecimal() and
        (int(message.text) <= MIN_AGE or int(message.text) > MAX_AGE)
    ):
        await message.answer('Пожалуйста, введите ваш настоящий возраст.')
        return

    # сохраняем пользователя
    USERS[message.from_user.id] = {
        **await state.get_data(),
        'age': int(message.text)
    }
    await state.clear()

    await send_message_and_sleep(
        message,
        f'{USERS[message.from_user.id]["name"]}, приятно познакомиться.'
    )
    await message.answer('Пожалуйста, выберите маршрут')
    await state.set_state(Route.route_selection)
