from aiogram import Router, types
from aiogram.filters.command import CommandStart
from aiogram.fsm import context
from core.logger import log_dec, logger_factory
from core.utils import answer_with_delay, reset_state
from db.crud import user_crud
from handlers.new_user import name_input
from handlers.route import route_selection
from sqlalchemy.ext.asyncio import AsyncSession

router = Router()
logger = logger_factory(__name__)

WELCOME = 'Добро пожаловать!'
GREETING = 'С возвращением, {}!'


@router.message(CommandStart())
@log_dec(logger)
async def cmd_start(
        message: types.Message,
        state: context.FSMContext,
        session: AsyncSession
):
    await reset_state(state, next_delay=0)
    # TODO: удалять накопленные inline-клавиатуры

    await answer_with_delay(message, state, WELCOME,
                            reply_markup=types.ReplyKeyboardRemove())

    user = await user_crud.get(message.from_user.id, session)
    if user and message.from_user.id == user.id:
        await answer_with_delay(message, state, GREETING.format(user.name), 2)
        await route_selection(message, state, session)
        return

    await name_input(message, state, session)
