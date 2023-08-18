from asyncio import sleep

from aiogram import F, Router
from aiogram.types import Message, ReplyKeyboardRemove

from keyboards.keyboards import route_select, yes_or_no
from test_data import Expo, Route, routes
from utils import route_data

router = Router()

expo = Expo
route = Route


@router.message(F.text.startswith('Маршрут'))
async def select_router(message: Message, delay: int = 5):
    route.way = message.text.split()[-1]
    route_info = routes[route.way]
    await route_data(route_info)
    await message.answer(
        route.description,
        reply_markup=ReplyKeyboardRemove()
    )
    await sleep(delay)
    await message.answer(
        route.welcome,
        reply_markup=yes_or_no(),
    )


@router.message(F.text.lower().startswith('новый'))
async def go_another_marshrut(message: Message):
    await message.answer('Выберете маршрут:', reply_markup=route_select())
