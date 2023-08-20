import re

from aiogram import F, Router, types
from aiogram.fsm import context
from core.logger import log_dec, logger_factory
from states import Route
from utils import send_message_and_sleep
from db.crud import route_crud
from sqlalchemy.ext.asyncio import AsyncSession

router = Router()
logger = logger_factory(__name__)


@router.message(Route.route_selection, F.text)
@log_dec(logger)
async def route_selection(
        message: types.Message,
        state: context.FSMContext,
        session: AsyncSession
):
    if await state.get_state() != Route.route_selection:
        await send_message_and_sleep(message, 'Пожалуйста, выберите маршрут.')
        await state.set_state(Route.route_selection)

        routes = await route_crud.get_all_by_attribute(
            {'is_active': True},
            session,
        )
        if routes:
            await message.answer('\n'.join([route.name for route in routes]))

        return

    await message.answer(f'Вы выбрали маршрут {message.text}')

