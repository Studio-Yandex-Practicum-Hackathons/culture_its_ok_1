from aiogram import Router, types
from aiogram.filters.command import Command
from aiogram.fsm import context

from core.logger import log_dec, logger_factory
from dummy_db import USERS
from keyboards.keyboards import route_select
from states import NewUser, Route
from utils import send_message_and_sleep

router = Router()
logger = logger_factory(__name__)


@router.message(Command('start'))
@log_dec(logger)
async def cmd_start(message: types.Message, state: context.FSMContext):
    await state.clear()
    await send_message_and_sleep(
        message,
        'Добро пожаловать',
        reply_markup=types.ReplyKeyboardRemove()
    )

    if message.from_user.id in USERS:
        await send_message_and_sleep(
            message,
            f'С возвращением, {USERS[message.from_user.id]["name"]}!'
        )
        await message.answer(
            'Пожалуйста, выберите маршрут.',
            reply_markup=route_select(),
        )
        await state.set_state(Route.route_selection)
        return

    await send_message_and_sleep(message, 'Давайте познакомимся')
    await message.answer('Пожалуйста, введите ваше имя')
    await state.set_state(NewUser.name_input)
