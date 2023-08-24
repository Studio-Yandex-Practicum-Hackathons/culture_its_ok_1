from aiogram import Router, types
from aiogram.filters.command import Command
from aiogram.fsm import context
from core.logger import log_dec, logger_factory
from db.crud import user_crud
from handlers.new_user import name_input
from handlers.route import route_selection
from sqlalchemy.ext.asyncio import AsyncSession
from core.utils import send_message_and_sleep

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
        await route_selection(message, state, session)
        return

    await name_input(message, state, session)
