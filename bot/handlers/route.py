import re
from datetime import datetime
from random import choice
from uuid import uuid4

from aiogram import F, Router, types
from aiogram.filters.command import Command
from aiogram.fsm import context
from core.config import VOICE_DIR, settings
from core.exceptions import LogicalError
from core.logger import log_dec, logger_factory
from core.states import Route
from core.storage import storage
from core.utils import (answer_photo_with_delay, answer_poll_with_delay,
                        answer_with_delay, delete_inline_keyboard,
                        delete_keyboard, parse_quiz, reset_state, trim_audio)
from db.crud import progress_crud, reflection_crud, route_crud, stage_crud
from keyboards.inline import (CALLBACK_NO, CALLBACK_YES,
                              get_one_button_inline_keyboard,
                              get_yes_no_inline_keyboard)
from keyboards.reply import get_reply_keyboard
from sqlalchemy.ext.asyncio import AsyncSession

router = Router()
logger = logger_factory(__name__)

MIN_RATE = 1
MAX_RATE = 10

FOUND_BUTTONS = [
    'Найдено!',
    'Найдено, всё в порядке!',
    'Я на месте',
    'Пришлось поискать',
]

# ----------------------
NO_ROUTES = 'К сожалению, на данный момент нет ни одного активного маршрута'
ROUTE_SELECTION = ('Выберите маршрут из списка ниже, чтобы посмотреть его '
                   'подробное описание')
START_MEDITATION = 'Начать медитацию'
ROUTE_START_POINT = 'Медитация начинается по адресу:\n{}'
MEDITATION_ENDED = ('На этом, медитация по маршруту «{}» окончена. '
                    'Спасибо, что провели это время с нами!')

RATE_ROUTE = ('Нам очень важна обратная связь наших пользователей. '
              'Пожалуйста, оцените пройденный маршрут по шкале от '
              f'{MIN_RATE} до {MAX_RATE}.')
WRONG_RATE = f'Пожалуйста, введите число от {MIN_RATE} до {MAX_RATE}.'
HIGH_RATE = 'Спасибо за столь высокую оценку нашей работы!'
MEDIUM_RATE = 'Спасибо за вашу оценку. Мы будем стараться быть лучше!'
LOW_RATE = 'Спасибо за вашу оценку. Жаль, что ваши ожидания не оправдались.'
# ----------------------


@router.message(Route.selection, F.text, ~Command(re.compile(r'^.+$')))
@log_dec(logger)
async def route_selection(
        message: types.Message,
        state: context.FSMContext,
        session: AsyncSession
):
    """Обработчик выбора маршрута пользователем. Формирует клавиатуру с
    маршрутами. Выводит информацию о маршруте при нажатии на соответствующую
    кнопку."""
    db_routes = await route_crud.get_all_by_attribute(
        {'is_active': True}, session, sort='id asc'
    )
    if not db_routes:
        await answer_with_delay(message, state, NO_ROUTES)
        return

    routes = {route.name: route for route in db_routes[:3] if route.stages}

    if await state.get_state() != Route.selection:
        await state.set_state(Route.selection)
        await answer_with_delay(
            message,
            state,
            ROUTE_SELECTION,
            reply_markup=get_reply_keyboard(*routes.keys(), adjust=1)
        )
        return

    if message.text in routes:
        current_route = routes[message.text]

        await answer_photo_with_delay(
            message,
            state,
            current_route.photo,
            current_route.description
        )
        await answer_with_delay(
            message,
            state,
            ROUTE_START_POINT.format(current_route.address),
            reply_markup=get_one_button_inline_keyboard(
                text=START_MEDITATION,
                callback_data=f'route${current_route.id}'
            )
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
    for stage in route.stages:
        for step in stage.steps:
            steps.append({**step.to_dict(), 'stage_id': stage.id})

    progress = await progress_crud.create(
        dict(
            user_id=callback.from_user.id,
            route_id=route_id,
            stage_id=steps[0]['stage_id'],
        ),
        session
    )

    await state.update_data({
        'route_id': route_id,
        'current_step': -1,
        'steps': steps,
        'progress_id': progress.id
    })

    await state.set_state(Route.following)
    await route_follow(callback.message, state, session)


@log_dec(logger)
async def route_follow(
        message: types.Message,
        state: context.FSMContext,
        session: AsyncSession
):
    """Функция проходит по цепочке шагов и отправляет пользователю сообщения,
    фотографии, кнопки, квизы и рефлексию."""
    state_data = await state.get_data()

    # нужно хранить последнее отправленное сообщение, чтобы управлять им
    last_message = None

    while True:
        if state_data['current_step'] + 1 >= len(state_data['steps']):
            # больше шагов нет, маршрут окончен
            break

        if await state.get_state() != Route.following:
            # если пользователь перезапустил бота, покидаем маршрут
            return

        state_data['current_step'] += 1
        await state.update_data({'current_step': state_data['current_step']})
        step = state_data['steps'][state_data['current_step']]

        # записали в БД текущий прогресс
        await progress_crud.update_by_attribute(
            {'id': state_data['progress_id']},
            {'stage_id': step['stage_id']},
            session
        )

        if step['type'] == 'text' and step['content']:
            last_message = await answer_with_delay(
                message, state, step['content'], step['delay_after_display']
            )
            continue

        if step['type'] == 'photo' and step['photo']:
            last_message = await answer_photo_with_delay(
                message, state, step['photo'], step['content'],
                step['delay_after_display']
            )
            continue

        if step['type'] == 'continue_button' and step['content']:
            if last_message is None:
                err_msg = 'Кнопке обязательно должно предшествовать сообщение'
                raise LogicalError(err_msg)

            keyboard = get_yes_no_inline_keyboard(*step['content'].split('\n'))
            await last_message.edit_reply_markup(reply_markup=keyboard)
            await state.update_data({**state_data, 'next_delay': 0})
            await state.set_state(Route.search)
            return

        if step['type'] == 'reflection' and step['content']:
            await answer_with_delay(message, state, step['content'])
            await state.update_data({**state_data, 'next_delay': 0})
            await state.set_state(Route.reflection)
            return

        if step['type'] == 'quiz' and step['content']:
            await answer_poll_with_delay(
                message, state, **parse_quiz(step['content'])
            )
            # костыль используется для передачи message и state в route_quiz
            storage.set_data(message, state)
            return

    if await state.get_state() != Route.following:
        # если пользователь перезапустил бота, покидаем маршрут
        return

    # маршрут окончен, сохраняем прогресс
    await progress_crud.update_by_attribute(
        {'id': state_data['progress_id']},
        {'finished_at': datetime.now()},
        session
    )
    route = await route_crud.get(state_data['route_id'], session)
    await answer_with_delay(message, state,
                            MEDITATION_ENDED.format(route.name))
    await route_rate(message, state, session)


@router.message(Route.reflection, F.text | F.voice)
@log_dec(logger)
async def route_reflection(
        message: types.Message,
        state: context.FSMContext,
        session: AsyncSession
):
    if message.text:
        answer = message.text[:settings.bot.reflection_text_limit]
        voice = None
    else:
        filename = (f'{uuid4()}+'
                    f'{datetime.now().strftime("%d.%m.%Y_%H-%M-%S")}.mp3')
        filepath = VOICE_DIR / filename
        await message.bot.download(message.voice, destination=filepath)
        trim_audio(str(filepath), settings.bot.reflection_voice_limit)
        answer = ''  # TODO: распознать голосовое сообщение
        voice = filename

    state_data = await state.get_data()
    step = state_data['steps'][state_data['current_step']]

    await reflection_crud.create(
        dict(
            user_id=message.from_user.id,
            route_id=state_data['route_id'],
            stage_id=step['stage_id'],
            question=step['content'],
            answer=answer,
            voice=voice
        ),
        session
    )
    await state.set_state(Route.following)
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
        await state.set_state(Route.following)
        await route_follow(callback.message, state, session)
    else:
        state_data = await state.get_data()
        step = state_data['steps'][state_data['current_step']]
        stage = await stage_crud.get(step['stage_id'], session)
        await answer_with_delay(
            callback.message,
            state,
            stage.how_to_get,
            reply_markup=get_one_button_inline_keyboard(
                choice(FOUND_BUTTONS), CALLBACK_YES
            ),
            next_delay=0
        )


@router.poll()
@log_dec(logger)
async def route_quiz(
        poll: types.Poll,
        message: types.Message,
        state: context.FSMContext,
        session: AsyncSession
):
    await state.set_state(Route.following)
    await route_follow(message, state, session)


@router.message(Route.rate, F.text)
@log_dec(logger)
async def route_rate(
        message: types.Message,
        state: context.FSMContext,
        session: AsyncSession
):
    if await state.get_state() != Route.rate:
        await state.set_state(Route.rate)
        await answer_with_delay(message, state, RATE_ROUTE)
        return

    if (
        not message.text.isdecimal() or
        (int(message.text) < MIN_RATE or int(message.text) > MAX_RATE)
    ):
        await answer_with_delay(message, state, WRONG_RATE)
        return

    rating = int(message.text)
    if rating < 4:
        await answer_with_delay(message, state, LOW_RATE)
    elif rating > 7:
        await answer_with_delay(message, state, HIGH_RATE)
    else:
        await answer_with_delay(message, state, MEDIUM_RATE)

    #  заносим оценку пользователя в таблицу прогресса
    state_data = await state.get_data()
    await progress_crud.update_by_attribute(
        {'id': state_data['progress_id']},
        {'rating': rating},
        session
    )

    await reset_state(state)
    await route_selection(message, state, session)
