from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder


def yes_or_no() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.button(text='Да')
    kb.button(text='Нет')
    kb.adjust(2)
    return kb.as_markup(resize_keyboard=True)


def find_object() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.button(text='Нашел')
    kb.button(text='Потерялся')
    kb.adjust(2)
    return kb.as_markup(resize_keyboard=True)


def find_button() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.button(text='Нашел')
    kb.adjust(1)
    return kb.as_markup(resize_keyboard=True)


def yes_button() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.button(text='Да')
    kb.adjust(1)
    return kb.as_markup(resize_keyboard=True)


def new_route() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.button(text='Новый маршрут')
    kb.adjust(1)
    return kb.as_markup(resize_keyboard=True)


def route_select() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.button(text='Маршрут 1')
    kb.button(text='Маршрут 2')
    kb.button(text='Маршрут 3')
    kb.adjust(3)
    return kb.as_markup(resize_keyboard=True)


def next_object() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.button(text='Отлично! Идем дальше')
    kb.adjust(1)
    return kb.as_markup(resize_keyboard=True)
