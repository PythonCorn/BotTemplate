from aiogram.filters.callback_data import CallbackData
from aiogram.utils.keyboard import InlineKeyboardBuilder


class StartCallbackData(CallbackData, prefix="start"):
    pass


def back_button(
    keyboard: InlineKeyboardBuilder,
    text: str = "Назад",
    callback_data: str | CallbackData = StartCallbackData.__prefix__,
) -> InlineKeyboardBuilder:
    keyboard.button(text=text, callback_data=callback_data)
    return keyboard
