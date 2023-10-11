from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton

CALLBACK_YES = 'ROUTE_YES'
CALLBACK_NO = 'ROUTE_NO'


def get_inline_keyboard(
        buttons: dict[str, str],
        adjust: int
):
    """
    Возвращает инлайн клавиатуру.
    :param buttons: словарь с кнопками клавиатуры, где:
        key - текст кнопки,
        value - возвращаемый ею колбэк
    :param adjust: параметр определяет количество кнопок в одном ряду
    """
    builder = InlineKeyboardBuilder()
    for text, callback in buttons.items():
        builder.add(InlineKeyboardButton(text=text, callback_data=callback))
    builder.adjust(adjust)
    return builder.as_markup()


def get_one_button_inline_keyboard(
        text: str,
        callback_data: str
):
    """Возвращает инлайн клавиатуру с одной кнопкой."""
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text=text, callback_data=callback_data))
    return builder.as_markup()


def get_yes_no_inline_keyboard(
        yes_text: str,
        no_text: str | None = None
):
    """Возвращает инлайн клавиатуру с одной или двумя кнопками. Колбэки кнопок
    предопределены константами."""
    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(text=yes_text, callback_data=CALLBACK_YES)
    )
    if no_text:
        builder.add(
            InlineKeyboardButton(text=no_text, callback_data=CALLBACK_NO)
        )
    return builder.as_markup()


def get_web_app_keyboard(
        text: str,
        web_app_info: str
):
    """Возвращает инлайн клавиатуру с одной кнопкой, которая открывает web app
    приложение."""
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text=text, web_app=web_app_info))
    return builder.as_markup()
