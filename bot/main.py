import asyncio

from core.config import settings
from core.logger import log_dec, logger_factory
from aiogram import Bot, Dispatcher
from handlers import start_router, new_user_router


@log_dec(logger=logger_factory(__name__))
async def main():
    bot = Bot(token=settings.bot.telegram_token)

    dispatcher = Dispatcher()
    dispatcher.include_routers(
        start_router,
        new_user_router
    )

    await bot.delete_webhook(drop_pending_updates=True)
    await dispatcher.start_polling(bot)


if __name__ == "__main__":
    settings.logging.init_global_logging_level()
    settings.sentry.init_sentry()

    asyncio.run(main())
