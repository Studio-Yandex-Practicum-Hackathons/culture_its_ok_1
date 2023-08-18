from asyncio import sleep

from aiogram import F, Router
from aiogram.types import Message

from keyboards.keyboards import new_route, next_object
from test_data import Expo, Route

router = Router()

expo = Expo
route = Route


@router.message(F.text)
async def get_reflection(message: Message, delay: int = 5):
    if expo.answer is not None:
        await message.answer(
            expo.answer
        )
        await sleep(delay)
    if expo.id == route.length:
        await message.answer(
            (
                'Команда фестиваля «Ничего страшного» будет '
                'рада вашему отклику! Для этого мы прикрепляем '
                'здесь небольшую форму, заполнение которой займёт '
                'не больше минуты:\n\n'
                '_Ссылка_'
            ),
        )
        await sleep(delay)
        await message.answer(
            'Вернуться к выбору маршрута?',
            reply_markup=new_route()
        )
    elif expo.step == 0:
        text = (
            'Нас ждут длительные переходы между локациями. '
            'Каждый раз, когда надо будет добраться до '
            'следующей точки маршрута, я буду спрашивать '
            'у Вас через определённое время получилось ли '
            'отыскать объект. Всё, что Вам нужно будет сделать, '
            'нажать кнопку «да» в случае достижения'
            'указанного адреса'
        )
        await message.answer(
            text,
            reply_markup=next_object(),
        )
    else:
        text = 'Пора двигаться к следующему экспонату.'
        await message.answer(text, reply_markup=next_object())
