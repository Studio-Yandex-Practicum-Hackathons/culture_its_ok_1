from datetime import datetime

from aiogram import F, Router, types
from aiogram.fsm import context
from core.exceptions import LogicalError
from core.logger import log_dec, logger_factory
from db.crud import progress_crud, route_crud
from keyboards.keyboards import (CALLBACK_NO, CALLBACK_YES, get_keyboard,
                                 get_one_button_inline_keyboard,
                                 get_yes_no_inline_keyboard)
from sqlalchemy.ext.asyncio import AsyncSession
from states import Route
from utils import (delete_inline_keyboard, delete_keyboard,
                   send_message_and_sleep, send_photo_and_sleep)

router = Router()
logger = logger_factory(__name__)

ROUTE_SELECTION = (
    'На выбор представлено три маршрута. Выберите любой, нажав '
    'кнопку ниже, чтобы посмотреть его подробное описание.'
)
ROUTE_START_POINT = 'Медитация начинается по адресу:\n{address}'


@router.message(Route.selection, F.text)
@log_dec(logger)
async def route_selection(
        message: types.Message,
        state: context.FSMContext,
        session: AsyncSession
):
    """Обработчик выбора маршрута пользователем. Формирует клавиатуру с
    маршрутами. Выводит информацию о маршруте при нажатии на соответствующую
    кнопку."""
    routes = {
        route.name: route for route in
        await route_crud.get_all_by_attribute(
            {'is_active': True},
            session,
            sort='id asc'
        )
        if route.objects
    }

    if await state.get_state() != Route.selection:
        await state.set_state(Route.selection)
        keyboard = get_keyboard(*routes.keys(), adjust=1)
        await message.answer(ROUTE_SELECTION, reply_markup=keyboard)
        return

    if message.text in routes:
        current_route = routes[message.text]

        keyboard = get_one_button_inline_keyboard(
            text='Начать медитацию', callback_data=f'route${current_route.id}'
        )

        await send_photo_and_sleep(message, current_route.photo)
        await send_message_and_sleep(message, current_route.description)
        await message.answer(
            ROUTE_START_POINT.format(address=current_route.address),
            reply_markup=keyboard
        )


@router.callback_query(Route.selection, F.data.startswith('route$'))
@log_dec(logger)
async def route_start(
        callback: types.CallbackQuery,
        state: context.FSMContext,
        session: AsyncSession
):
    """Обработчик запуска прохождения маршрута. Принимает колбэк с id
    выбранного пользователем маршрута. Готовит цепочку шагов и запускает их
    прохождение."""
    await delete_keyboard(callback.message)
    await delete_inline_keyboard(callback.message)
    await callback.answer()

    route_id = int(callback.data.split("$")[1])
    route = await route_crud.get(route_id, session)

    steps = []
    for _object in route.objects:
        for step in _object.steps:
            step.object_id = _object.id
            steps.append(step)

    progress = dict(
        user_id=callback.from_user.id,
        route_id=route_id,
        object_id=steps[0].object_id,
    )
    progress_db = await progress_crud.create(progress, session)

    await state.set_data({
        'route_id': route_id,
        'current_step': 0,
        'steps': steps,
        'progress_id': progress_db.id
    })

    await route_follow(callback.message, state, session)


@log_dec(logger)
async def route_follow(
        message: types.Message,
        state: context.FSMContext,
        session: AsyncSession
):
    """Функция проходит по цепочке шагов и отправляет пользователю сообщения"""
    await state.set_state(Route.following)

    state_data = await state.get_data()

    # нужно хранить последнее отправленное сообщение, чтобы редактировать у
    # него inline-кнопки
    last_message = None

    while state_data['current_step'] < len(state_data['steps']):
        step = state_data['steps'][state_data['current_step']]
        state_data['current_step'] += 1

        # записали в БД текущий прогресс
        await progress_crud.update_by_attribute(
            {'id': state_data['progress_id']},
            {'object_id': step.object_id},
            session
        )

        if step.type == 'text':
            last_message = await send_message_and_sleep(
                message, step.content, step.delay_after_display
            )
            continue

        if step.type == 'photo':
            last_message = await send_photo_and_sleep(
                message, step.photo, step.delay_after_display
            )
            continue

        if step.type == 'continue_button':
            keyboard = get_yes_no_inline_keyboard(*step.content.split('\n'))
            if last_message is None:
                err_msg = 'Кнопке обязательно должно предшествовать сообщение'
                raise LogicalError(err_msg)

            await last_message.edit_reply_markup(reply_markup=keyboard)
            await state.set_state(Route.search)
            await state.set_data(state_data)
            return

        if step.type == 'reflection':
            await message.answer(step.content)
            await state.set_state(Route.reflection)
            await state.set_data(state_data)
            return

    # маршрут окончен, сохраняем прогресс и очищаем состояние
    await progress_crud.update_by_attribute(
        {'id': state_data['progress_id']},
        {'finished_at': datetime.now()},
        session
    )
    await state.clear()

    await route_selection(message, state, session)


@router.message(Route.reflection, F.text | F.voice)
@log_dec(logger)
async def route_reflection(
        message: types.Message,
        state: context.FSMContext,
        session: AsyncSession
):
    # TODO: сохраняем рефлексию в базу
    await route_follow(message, state, session)


@router.callback_query(Route.search, F.data.in_({CALLBACK_YES, CALLBACK_NO}))
@log_dec(logger)
async def route_search(
        callback: types.CallbackQuery,
        state: context.FSMContext,
        session: AsyncSession
):
    await delete_inline_keyboard(callback.message)
    await callback.answer()

    if callback.data == CALLBACK_YES:
        await route_follow(callback.message, state, session)
    else:
        # TODO: даём пользователю больше информации о местоположении объекта
        pass
