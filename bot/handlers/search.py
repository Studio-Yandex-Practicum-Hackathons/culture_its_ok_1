from aiogram import F, Router
from aiogram.types import Message

from keyboards.keyboards import find_button, yes_button
from test_data import Expo, Route

router = Router()

expo = Expo
route = Route


@router.message(F.text.lower() == 'нет')
async def cant_find_route(message: Message):
    await message.answer(
        (
            f'Медитация начинается по адресу {route.address}.\n'
            f'Чтобы пройти к началу маршрута, предлагаю воспользоваться '
            f'<a href="{route.url}">Яндекс.картами.</a>'
        ),
        disable_web_page_preview=True,
        reply_markup=yes_button(),
    )


@router.message(F.text.lower() == 'потерялся')
async def how_to_get(message: Message):
    await message.answer(
        f'Объект находится по адресу {expo.address}.\n{expo.how_to_get}\n\n'
        f'<a href="{expo.url}">Яндекс.карты.</a>',
        reply_markup=find_button(),
    )
