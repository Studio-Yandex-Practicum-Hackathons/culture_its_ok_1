from aiogram import F, Router, types
from aiogram.fsm import context
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from core.logger import log_dec, logger_factory
from db.crud import route_crud
from sqlalchemy.ext.asyncio import AsyncSession
from states import Route

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
        await state.set_state(Route.route_selection)

        routes = await route_crud.get_all_by_attribute(
            {'is_active': True},
            session,
        )

        builder = ReplyKeyboardBuilder()
        for i, route in enumerate(routes):
            builder.add(types.KeyboardButton(text=route.name))
        builder.adjust(1)

        await message.answer(
            'Пожалуйста, выберите маршрут',
            reply_markup=builder.as_markup(resize_keyboard=True),
        )
        return

    routes = {
        route.name: route for route in
        await route_crud.get_all_by_attribute(
            {'is_active': True},
            session,
        )
    }
    if message.text in routes:
        await state.set_data(dict(route=routes[message.text]))
        # тут будет обработка выбранного маршрута
