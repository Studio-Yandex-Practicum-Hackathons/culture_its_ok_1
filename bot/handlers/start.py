from aiogram import Router, types
from aiogram.filters.command import Command
from core.logger import log_dec, logger_factory

router = Router()
logger = logger_factory(__name__)


@router.message(Command("start"))
@log_dec(logger)
async def cmd_start(message: types.Message):
    await message.answer("Бот начал работу")
