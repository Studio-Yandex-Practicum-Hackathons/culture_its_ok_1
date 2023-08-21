from aiogram import F, Router, types
from aiogram.fsm import context
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from core.logger import log_dec, logger_factory
from db.crud import route_crud
from sqlalchemy.ext.asyncio import AsyncSession
from states import Route
from utils import send_message_and_sleep, send_photo_and_sleep

router = Router()
logger = logger_factory(__name__)

ROUTE_SELECTION = (
    'На выбор представлено три маршрута. Выберите любой, нажав '
    'кнопку ниже, чтобы посмотреть его подробное описание.'
)
ROUTE_START_POINT = 'Медитация начинается по адресу:\n{address}'


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
            sort='id asc'
        )

        builder = ReplyKeyboardBuilder()
        for i, route in enumerate(routes):
            builder.add(types.KeyboardButton(text=route.name))
        builder.adjust(1)

        await message.answer(
            ROUTE_SELECTION,
            reply_markup=builder.as_markup(resize_keyboard=True),
        )
        return

    routes = {
        route.name: route for route in
        await route_crud.get_all_by_attribute(
            {'is_active': True},
            session
        )
    }
    if message.text in routes:
        current_route = routes[message.text]

        builder = InlineKeyboardBuilder()
        builder.row(types.InlineKeyboardButton(
            text="Начать медитацию",
            callback_data=f'route${current_route.id}')
        )

        await send_photo_and_sleep(message, current_route.photo)
        await send_message_and_sleep(message, current_route.description)
        await send_message_and_sleep(
            message,
            ROUTE_START_POINT.format(address=current_route.address),
            reply_markup=builder.as_markup()
        )


@router.callback_query(Route.route_selection)
async def route_start(
        callback: types.CallbackQuery,
        state: context.FSMContext
):
    current_route = callback.data.split("$")[1]
    await callback.answer()

    await state.set_data({
        'current_route': current_route,
        'current_object': 0,
        'current_step': 0
    })
    print(f'Выбран маршрут {current_route}')
    # отсюда начинается прохождение маршрута
