from aiogram import F, Router, types
from aiogram.fsm import context
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from core.logger import log_dec, logger_factory
from db.crud import route_crud
from sqlalchemy.ext.asyncio import AsyncSession
from states import Route
from utils import send_message_and_sleep, send_photo_and_sleep, delete_keyboard
from aiogram.utils.markdown import hide_link
from db.dummy import get_next_step


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

        urls = {
            'Руки бы им всем оторвать': 'https://yandex.ru/maps/-/CDQAaR2c',
            'Не с кем играть. Играю со стенкой': 'https://yandex.ru/maps/-/CDQ4ZJ7W',
            '...но спи/СМИ спокойно': 'https://yandex.ru/maps/-/CDQ4ZR2O',
        }
        await send_photo_and_sleep(message, current_route.photo)
        await send_message_and_sleep(message, current_route.description, 5)
        await send_message_and_sleep(
            message,
            ROUTE_START_POINT.format(address=current_route.address) + hide_link(urls[current_route.name]),
            reply_markup=builder.as_markup()
        )


@router.callback_query(Route.route_selection)
async def route_start(
        callback: types.CallbackQuery,
        state: context.FSMContext
):
    await delete_keyboard(callback.message)

    current_route = callback.data.split("$")[1]
    await state.set_data({
        'current_route': current_route,
        'current_object': 0,
        'current_step': 0
    })
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.answer()
    await keep_going(callback.message, state)


async def keep_going(
        message: types.Message,
        state: context.FSMContext,
):
    if await state.get_state() != Route.route_passing:
        await state.set_state(Route.route_passing)

    async for step in get_next_step():
        if step['type'] == 'text':
            await send_message_and_sleep(message, step['content'], step['delay'], reply_markup=types.ReplyKeyboardRemove())

        if step['type'] == 'photo':
            await send_photo_and_sleep(message, step['content'], step['delay'], reply_markup=types.ReplyKeyboardRemove())

        if step['type'] == 'continue_button':
            text, buttons = step['content'].split('$')
            builder = InlineKeyboardBuilder()
            for button in buttons.split('/'):
                builder.add(
                    types.InlineKeyboardButton(
                        text=button,
                        callback_data='123')
                    )
            await send_message_and_sleep(message, text, step['delay'], reply_markup=builder.as_markup())
            return

        if step['type'] == 'reflection':
            await send_message_and_sleep(message, step['content'], step['delay'], reply_markup=types.ReplyKeyboardRemove())
            await state.set_state(Route.reflection)
            return


@router.message(Route.reflection, F.text | F.voice)
@log_dec(logger)
async def route_reflection(
        message: types.Message,
        state: context.FSMContext,
        session: AsyncSession
):
    # сохраняем рефлексию в базу
    await keep_going(message, state)


@router.callback_query(Route.route_passing)
@log_dec(logger)
async def route_passing(
        callback: types.CallbackQuery,
        state: context.FSMContext,
):
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.answer()
    await keep_going(callback.message, state)



