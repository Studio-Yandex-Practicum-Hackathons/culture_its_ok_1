from aiogram.utils.keyboard import KeyboardButton, ReplyKeyboardBuilder


def get_reply_keyboard(
        *args,
        adjust: int
):
    """
    Возвращает клавиатуру с обычными кнопками
    :param args: список текстовых значений на кнопках
    :param adjust: определяет количество кнопок в ряду
    """
    builder = ReplyKeyboardBuilder()
    for button_text in args:
        builder.add(KeyboardButton(text=button_text))
    builder.adjust(adjust)
    return builder.as_markup(resize_keyboard=True)
