import re

from aiogram import F, Router, types
from aiogram.fsm import context
from core.logger import log_dec, logger_factory
from core.states import NewUser
from core.utils import send_message_and_sleep
from db.crud import user_crud
from handlers.route import route_selection
from sqlalchemy.ext.asyncio import AsyncSession

router = Router()
logger = logger_factory(__name__)

MIN_NAME_LENGTH = 2
MAX_NAME_LENGTH = 30

MIN_AGE = 2
MAX_AGE = 125


@router.message(NewUser.name_input, F.text)
@log_dec(logger)
async def name_input(
        message: types.Message,
        state: context.FSMContext,
        session: AsyncSession
):
    if await state.get_state() != NewUser.name_input:
        await send_message_and_sleep(message, 'Давайте познакомимся')
        await message.answer('Пожалуйста, введите ваше имя')
        await state.set_state(NewUser.name_input)
        return

    pattern = rf'^\D{{{MIN_NAME_LENGTH},{MAX_NAME_LENGTH}}}$'
    if not re.match(pattern, message.text):
        await message.answer('Пожалуйста, введите ваше настоящее имя.')
        return

    await state.set_data(dict(name=message.text))
    await age_input(message, state, session)


@router.message(NewUser.age_input, F.text)
@log_dec(logger)
async def age_input(
        message: types.Message,
        state: context.FSMContext,
        session: AsyncSession
):
    if await state.get_state() != NewUser.age_input:
        await message.answer('Пожалуйста, введите ваш возраст.')
        await state.set_state(NewUser.age_input)
        return

    if (
        not message.text.isdecimal() or
        message.text.isdecimal() and
        (int(message.text) <= MIN_AGE or int(message.text) > MAX_AGE)
    ):
        await message.answer('Пожалуйста, введите ваш настоящий возраст.')
        return

    # сохраняем пользователя
    user = {
        'id': message.from_user.id,
        **await state.get_data(),
        'age': int(message.text)
    }
    await user_crud.create(user, session)

    await send_message_and_sleep(
        message,
        f'{user["name"]}, приятно познакомиться.'
    )

    await state.clear()
    await route_selection(message, state, session)
