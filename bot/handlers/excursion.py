from asyncio import sleep

from aiogram import F, Router
from aiogram.types import Message, ReplyKeyboardRemove

from handlers.reflection import get_reflection
from keyboards.keyboards import find_object
from test_data import Expo, Route, routes
from utils import expo_data

router = Router()
expo = Expo
route = Route


@router.message(F.text.lower() == 'да')
async def start_route(message: Message):
    await message.answer(
        'Отлично, тогда начнём нашу медитацию!', reply_markup=ReplyKeyboardRemove()
    )
    expo.step = 0
    expo_info = route.objects[expo.step]
    await expo_data(expo_info)
    await start_object(message)


async def start_object(message: Message):
    await message.answer_photo(
        expo.photo,
        f'Название работы: {expo.name}\n'
        f'Автор: {expo.author}\n\n'
        f'Удалось найти объект?',
        reply_markup=find_object(),
    )


@router.message(F.text.lower() == 'нашел')
async def excursion(message: Message, delay: int = 10):
    if expo.prologue is not None:
        await message.answer(
            expo.prologue,
            reply_markup=ReplyKeyboardRemove(),
        )
        await sleep(delay)
    if expo.description is not None:
        await message.answer(
            expo.description,
        )
        await sleep(delay)
    if expo.reflection is not None:
        await message.answer(
            expo.reflection,
        )
    else:
        await get_reflection(message)


@router.message(F.text.lower().startswith('отлично'))
async def next_obj(message: Message):
    expo.step += 1
    expo_info = routes[route.way]['objects'][expo.step]
    expo.id = expo_info['id']
    expo.name = expo_info['name']
    expo.author = expo_info['author']
    expo.address = expo_info['address']
    expo.url = expo_info['url']
    expo.how_to_get = expo_info['how_to_get']
    expo.photo = expo_info['photo']
    try:
        expo.prologue = expo_info['prologue']
    except:
        expo.prologue = None
    try:
        expo.description = expo_info['description']
    except:
        expo.description = None
    try:
        expo.reflection = expo_info['reflection']
    except:
        expo.reflection = None
    try:
        expo.answer = expo_info['answer']
    except:
        expo.answer = None
    await message.answer_photo(
        expo.photo,
        f'Следующий объект расположен по адресу {expo.address}.\nПолучилось найти объект?',
        reply_markup=find_object(),
    )
