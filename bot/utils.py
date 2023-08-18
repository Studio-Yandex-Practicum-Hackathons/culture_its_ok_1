from asyncio import sleep

from aiogram import types

from test_data import Expo, Route

expo = Expo
route = Route

async def send_message_and_sleep(
    message: types.Message,
    text: str,
    delay: int = 1,
    **kwargs
):
    await message.answer(text, **kwargs)
    await sleep(delay)


async def expo_data(expo_info):
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


async def route_data(route_info):
    route.length = len(route_info['objects'])
    route.id = route_info['id']
    route.address = route_info['address']
    route.welcome = route_info['welcome']
    route.objects = route_info['objects']
    route.url = route_info['url']
    route.description = route_info['description']
