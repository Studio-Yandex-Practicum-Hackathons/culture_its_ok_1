from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from core.storage import storage
from db.postgres import get_async_session


class SessionMiddleware(BaseMiddleware):
    """Этот middleware добавляет в переменные объект асинхронной сессии."""
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        a_gen = get_async_session()
        data['session'] = await anext(a_gen)
        return await handler(event, data)


class StateMessageMiddleware(BaseMiddleware):
    """Этот middleware добавляет в переменные объекты класса Message и
    FSMContext. Класс используется только для обработчика dispatcher.poll, т.к.
    aiogram по-умолчанию не передаёт в него эти объекты."""
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        data['message'], data['state'] = storage.get_data()
        return await handler(event, data)
