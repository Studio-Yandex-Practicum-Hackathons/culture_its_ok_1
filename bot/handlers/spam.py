from aiogram import F, Router, types
from core.logger import log_dec, logger_factory


router = Router()
logger = logger_factory(__name__)

WARNING_TEXT = (
    'Для удобства общения, пожалуйста, '
    'используйте кнопки, или дождитесь ответа.'
)

class Counter:
    def __init__(self):
        self.spam_count = None

counter = Counter()

@router.message(F.text)
@log_dec(logger)
async def unexpected_message(message: types.Message):
    if counter.spam_count is None:
        counter.spam_count = 0
    counter.spam_count += 1
    if counter.spam_count > 1:
        await null_count()
        await message.answer(WARNING_TEXT)

async def null_count():
    counter.spam_count = 0
