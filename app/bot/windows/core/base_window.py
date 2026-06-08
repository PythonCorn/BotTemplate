from aiogram.types import InlineKeyboardMarkup, ReplyKeyboardMarkup
from aiogram.utils.i18n import I18n
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.bot.windows.core.window_message import WindowMessage


class BaseWindow:
    def __init__(self, i18n: I18n, locale: str = "ru") -> None:
        self.i18n = i18n
        self.locale = locale

    @staticmethod
    def get_empty_keyboard() -> InlineKeyboardBuilder:
        return InlineKeyboardBuilder()

    @staticmethod
    def message(
        text: str = "",
        caption: str = "",
        reply_markup: InlineKeyboardMarkup | ReplyKeyboardMarkup | None = None,
        photo_filename: str | None = None,
    ) -> WindowMessage:
        return WindowMessage(
            text=text, caption=caption, reply_markup=reply_markup, photo_filename=photo_filename
        )

    def _(self, text: str, **kwargs) -> str:
        translated = self.i18n.gettext(text, locale=self.locale)

        if kwargs:
            return translated.format(**kwargs)

        return translated
