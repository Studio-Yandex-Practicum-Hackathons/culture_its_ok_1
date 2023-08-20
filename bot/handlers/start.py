from aiogram import Router, types
from aiogram.filters.command import Command
from aiogram.fsm import context
from core.logger import log_dec, logger_factory
from states import NewUser, Route
from utils import send_message_and_sleep
from db.crud import user_crud, route_crud
from sqlalchemy.ext.asyncio import AsyncSession

router = Router()
logger = logger_factory(__name__)


@router.message(Command('start'))
@log_dec(logger)
async def cmd_start(
        message: types.Message,
        state: context.FSMContext,
        session: AsyncSession
):
    await state.clear()
    await send_message_and_sleep(
        message,
        'Добро пожаловать',
        reply_markup=types.ReplyKeyboardRemove()
    )

    user = await user_crud.get(message.from_user.id, session)
    if user and message.from_user.id == user.id:
        await send_message_and_sleep(message, f'С возвращением, {user.name}!')
        await send_message_and_sleep(message, 'Пожалуйста, выберите маршрут.')
        await state.set_state(Route.route_selection)
        routes = await route_crud.get_all_by_attribute(
            {'is_active': True},
            session,
        )
        routes_to_show = '\n'.join([route.name for route in routes])
        if routes_to_show:
            await message.answer(routes_to_show)
        return

    await send_message_and_sleep(message, 'Давайте познакомимся')
    await message.answer('Пожалуйста, введите ваше имя')
    await state.set_state(NewUser.name_input)
