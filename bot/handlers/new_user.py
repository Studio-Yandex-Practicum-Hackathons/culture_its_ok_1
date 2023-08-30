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

MIN_AGE = 3
MAX_AGE = 125

# ----------------------
ACQUAINTANCE = 'Давайте познакомимся.'
ENTER_NAME = 'Пожалуйста, введите ваше имя.'
ENTER_REAL_NAME = 'Пожалуйста, введите ваше настоящее имя.'
ENTER_AGE = 'Пожалуйста, введите ваш возраст.'
ENTER_REAL_AGE = 'Пожалуйста, введите ваш настоящий возраст.'
ENTER_HOBBIES = ('Пожалуйста, укажите через запятую несколько из ваших '
                 'увлечений, хобби')
NICE_TO_MEET = '{}, приятно познакомиться!'
# ----------------------


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

    await state.update_data({'user_name': message.text.strip()})
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
        (int(message.text) < MIN_AGE or int(message.text) > MAX_AGE)
    ):
        await answer_with_delay(message, state, ENTER_REAL_AGE)
        return

    await state.update_data({'user_age': int(message.text)})
    await hobby_input(message, state, session)


@router.message(NewUser.hobby_input, F.text)
@log_dec(logger)
async def hobby_input(
        message: types.Message,
        state: context.FSMContext,
        session: AsyncSession
):
    if await state.get_state() != NewUser.hobby_input:
        await answer_with_delay(message, state, ENTER_HOBBIES)
        await state.set_state(NewUser.hobby_input)
        return

    interests = message.text.strip()
    if interests:
        # сохраняем пользователя
        state_data = await state.get_data()
        user = {
            'id': message.from_user.id,
            'name': state_data['user_name'],
            'age': state_data['user_age'],
            'interests': interests
        }
        await user_crud.create(user, session)

        await answer_with_delay(message, state,
                                NICE_TO_MEET.format(user['name']))
        await reset_state(state, next_delay=2)
        await route_selection(message, state, session)
