from aiogram import F, Router, types
from aiogram.filters.command import CommandStart
from aiogram.fsm import context
from core.logger import log_exceptions, logger_factory
from core.states import Route
from core.utils import (CHAT_ACTION_PERIOD, answer_with_delay,
                        delete_inline_keyboard, reset_state, sleep)
from db.crud import route_crud, user_crud
from handlers.new_user import name_input
from handlers.route import route_follow, route_selection
from handlers.spam import spam_counter
from keyboards.inline import get_inline_keyboard
from sqlalchemy.ext.asyncio import AsyncSession

router = Router()
logger = logger_factory(__name__)

CALLBACK_CONTINUE = 'CONTINUE_ROUTE'
CALLBACK_RESET = 'RESET_ROUTE'
ROUTE_CONTINUATION_BUTTONS = {
    'Хочу продолжить': CALLBACK_CONTINUE,
    'Начну заново': CALLBACK_RESET
}

# ----------------------
WELCOME = 'Добро пожаловать!'
BOT_INFO = ('Бот проведёт для вас экскурсию-медитацию по маршрутам с работами '
            'современных уличных художников.')
GREETING = 'С возвращением, {}!'
CONTINUE_ROUTE = ('Мы обнаружили, что вы недавно начали, но не завершили '
                  'маршрут "{}". Желаете продолжить с прерванного места или '
                  'хотите начать заново этот или другой маршрут?')
# ----------------------


@router.message(CommandStart())
@log_exceptions(logger)
async def cmd_start(
        message: types.Message,
        state: context.FSMContext,
        session: AsyncSession
):
    """Функция обрабатывает команду /start."""
    spam_counter.reset()
    await state.set_state(state=None)
    await state.update_data({'next_delay': 0})

    await answer_with_delay(message, state, WELCOME,
                            reply_markup=types.ReplyKeyboardRemove())

    user = await user_crud.get(message.from_user.id, session)
    if user and message.from_user.id == user.id:
        await answer_with_delay(message, state, GREETING.format(user.name))

        # проверяем, существует ли незаконченный маршрут
        state_data = await state.get_data()
        current_step = state_data.get('current_step')
        if current_step and current_step < len(state_data['steps']):
            route = await route_crud.get(state_data['route_id'], session)
            await answer_with_delay(
                message,
                state,
                CONTINUE_ROUTE.format(route.name),
                reply_markup=get_inline_keyboard(ROUTE_CONTINUATION_BUTTONS, 2),  # noqa: E501
                next_delay=0
            )
            return

        await route_selection(message, state, session)
        return

    await answer_with_delay(message, state, BOT_INFO, 2)
    await name_input(message, state, session)


@router.callback_query(F.data.in_({CALLBACK_CONTINUE, CALLBACK_RESET}))
@log_exceptions(logger)
async def route_start(
        callback: types.CallbackQuery,
        state: context.FSMContext,
        session: AsyncSession
):
    """Функция обрабатывает ответ пользователя на предложение продолжить
    прерванный маршрут или перейти к выбору маршрутов, чтобы начать заново."""
    spam_counter.reset()
    await delete_inline_keyboard(callback.message)

    if callback.data == CALLBACK_CONTINUE:
        state_data = await state.get_data()
        current_step = state_data['current_step']
        if state_data['steps'][current_step]['type'] == 'continue_button':
            # если пользователь прервал маршрут перед получением инлайн кнопок,
            # откатываемся на два шага назад, чтобы отправить сообщение, к
            # которому эти кнопки привязываются
            current_step -= 2
        else:
            # откатываемся на шаг назад, т.к. функция хождения по маршруту
            # увеличивает current_step перед отправкой очередного сообщения
            current_step -= 1
        await state.update_data({'current_step': max(current_step, 0)})
        await state.set_state(Route.following)
        await sleep(CHAT_ACTION_PERIOD)
        await route_follow(callback.message, state, session)
        return

    # пользователь решил начать заново
    await reset_state(state, next_delay=0)
    await route_selection(callback.message, state, session)
