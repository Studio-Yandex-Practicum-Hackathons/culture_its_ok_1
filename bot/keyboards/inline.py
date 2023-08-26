from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton

CALLBACK_YES = 'ROUTE_YES'
CALLBACK_NO = 'ROUTE_NO'


def get_inline_keyboard(
        buttons: dict[str, str],
        adjust: int
):
    builder = InlineKeyboardBuilder()
    for text, callback in buttons.items():
        builder.add(InlineKeyboardButton(text=text, callback_data=callback))
    builder.adjust(adjust)
    return builder.as_markup()


def get_one_button_inline_keyboard(
        text: str,
        callback_data: str
):
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text=text, callback_data=callback_data))
    return builder.as_markup()


def get_yes_no_inline_keyboard(
        yes_text: str,
        no_text: str | None = None
):
    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(text=yes_text, callback_data=CALLBACK_YES)
    )
    if no_text:
        builder.add(
            InlineKeyboardButton(text=no_text, callback_data=CALLBACK_NO)
        )
    return builder.as_markup()
