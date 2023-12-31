import asyncio

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage
from core.config import settings
from core.logger import log_exceptions, logger_factory
from core.middleware import SessionMiddleware, StateMessageMiddleware
from handlers import (admin_router, new_user_router, route_router, spam_router,
                      start_router)
from redis.asyncio import Redis


@log_exceptions(logger=logger_factory(__name__))
async def main():
    """Функция инициализации и запуска бота."""
    bot = Bot(token=settings.bot.telegram_token, parse_mode='html')

    dispatcher = Dispatcher(
        storage=RedisStorage(
            Redis(host=settings.redis.host, port=settings.redis.port),
            state_ttl=settings.bot.storage_ttl,
            data_ttl=settings.bot.storage_ttl
        )
    )
    dispatcher.message.middleware(SessionMiddleware())
    dispatcher.callback_query.middleware(SessionMiddleware())
    dispatcher.poll.middleware(SessionMiddleware())
    dispatcher.poll.middleware(StateMessageMiddleware())
    dispatcher.include_routers(
        start_router,
        new_user_router,
        route_router,
        admin_router,
        spam_router
    )

    await bot.delete_webhook(drop_pending_updates=True)
    await dispatcher.start_polling(bot)


if __name__ == "__main__":
    settings.sentry.init_sentry()

    asyncio.run(main())
