from aiogram import Router, types
from aiogram.filters.command import CommandStart
from aiogram.fsm import context
from core.logger import log_exceptions, logger_factory
from core.utils import answer_with_delay, reset_state
from db.crud import user_crud
from handlers.new_user import name_input
from handlers.route import route_selection
from sqlalchemy.ext.asyncio import AsyncSession
from handlers.spam import spam_counter

router = Router()
logger = logger_factory(__name__)

# ----------------------
WELCOME = 'Добро пожаловать!'
BOT_INFO = ('Бот проведёт для вас экскурсию-медитацию по маршрутам с работами '
            'современных уличных художников.')
GREETING = 'С возвращением, {}!'
# ----------------------


@router.message(CommandStart())
@log_exceptions(logger)
async def cmd_start(
        message: types.Message,
        state: context.FSMContext,
        session: AsyncSession
):
    spam_counter.reset()
    await state.update_data({'next_delay': 0})
    # TODO: удалять накопленные inline-клавиатуры

    await answer_with_delay(message, state, WELCOME,
                            reply_markup=types.ReplyKeyboardRemove())

    user = await user_crud.get(message.from_user.id, session)
    if user and message.from_user.id == user.id:
        await answer_with_delay(message, state, GREETING.format(user.name))
        # state_data = await state.get_data()
        # if state_data.get('current_step') and state_data['current_step'] < state_data['steps']:
        #     await answer_with_delay(message, state, 'Обнаружен незавершённый маршрут')
        await route_selection(message, state, session)
        return

    await answer_with_delay(message, state, BOT_INFO, 2)
    await name_input(message, state, session)
