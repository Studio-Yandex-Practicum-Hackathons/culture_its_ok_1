import re

from aiogram import F, Router, types
from aiogram.fsm import context
from core.logger import log_dec, logger_factory
from core.states import NewUser
from core.utils import answer_with_delay, reset_state
from db.crud import user_crud
from handlers.route import route_selection
from sqlalchemy.ext.asyncio import AsyncSession

router = Router()
logger = logger_factory(__name__)

MIN_NAME_LENGTH = 2
MAX_NAME_LENGTH = 30

MIN_AGE = 2
MAX_AGE = 125

ACQUAINTANCE = 'Давайте познакомимся.'
ENTER_NAME = 'Пожалуйста, введите ваше имя.'
ENTER_REAL_NAME = 'Пожалуйста, введите ваше настоящее имя.'
ENTER_AGE = 'Пожалуйста, введите ваш возраст.'
ENTER_REAL_AGE = 'Пожалуйста, введите ваш настоящий возраст.'
NICE_TO_MEET = '{}, приятно познакомиться!'


@router.message(NewUser.name_input, F.text)
@log_dec(logger)
async def name_input(
        message: types.Message,
        state: context.FSMContext,
        session: AsyncSession
):
    if await state.get_state() != NewUser.name_input:
        await answer_with_delay(message, state, ACQUAINTANCE)
        await answer_with_delay(message, state, ENTER_NAME)
        await state.set_state(NewUser.name_input)
        return

    pattern = rf'^\D{{{MIN_NAME_LENGTH},{MAX_NAME_LENGTH}}}$'
    if not re.match(pattern, message.text):
        await answer_with_delay(message, state, ENTER_REAL_NAME)
        return

    await state.update_data({'user': dict(name=message.text)})
    await age_input(message, state, session)


@router.message(NewUser.age_input, F.text)
@log_dec(logger)
async def age_input(
        message: types.Message,
        state: context.FSMContext,
        session: AsyncSession
):
    if await state.get_state() != NewUser.age_input:
        await answer_with_delay(message, state, ENTER_AGE)
        await state.set_state(NewUser.age_input)
        return

    if (
        not message.text.isdecimal() or
        message.text.isdecimal() and
        (int(message.text) <= MIN_AGE or int(message.text) > MAX_AGE)
    ):
        await answer_with_delay(message, state, ENTER_REAL_AGE)
        return

    # сохраняем пользователя
    state_data = await state.get_data()
    user = {
        'id': message.from_user.id,
        **state_data['user'],
        'age': int(message.text)
    }
    await user_crud.create(user, session)

    await answer_with_delay(message, state, NICE_TO_MEET.format(user['name']))
    await reset_state(state, next_delay=2)
    await route_selection(message, state, session)
