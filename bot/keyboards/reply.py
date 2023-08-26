from aiogram.utils.keyboard import KeyboardButton, ReplyKeyboardBuilder


def get_reply_keyboard(
        *args,
        adjust: int
):
    builder = ReplyKeyboardBuilder()
    for button_text in args:
        builder.add(KeyboardButton(text=button_text))
    builder.adjust(adjust)
    return builder.as_markup(resize_keyboard=True)
