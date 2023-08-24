from aiogram import F, Router, types
from aiogram.fsm import context
from core.logger import log_dec, logger_factory
from states import Route

router = Router()
logger = logger_factory(__name__)

WARNING_TEXT = 'Предупреждающий текст!'
MAX_TRY = 1  # Максимальное число попыток введения текста.


class Counter:
    def __init__(self, spam_count):
        self.spam_count = spam_count


counter = Counter


@router.message(Route.selection, Route.following, Route.search, F.text)
@log_dec(logger)
async def route_selection(
    message: types.Message,
    state: context.FSMContext,
):
    if (
        await state.get_state() == Route.selection
        or await state.get_state() == Route.search
        or await state.get_state() == Route.following
    ):
        try:
            counter.spam_count += 1
        except AttributeError:
            counter.spam_count = 1
        if counter.spam_count > MAX_TRY:
            counter.spam_count = 0
            await message.answer(WARNING_TEXT)
