from typing import TYPE_CHECKING

from aiogram.types import InlineKeyboardMarkup, ReplyKeyboardMarkup
from aiogram.utils.i18n import I18n
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.bot.windows.core.window_message import WindowMessage

if TYPE_CHECKING:
    from app.bot.windows.core.container import Windows


class BaseWindow:
    def __init__(self, windows: "Windows"):
        self.windows = windows

    @property
    def locale(self):
        return self.windows.locale

    @property
    def i18n(self) -> I18n | None:
        return self.windows.i18n

    @staticmethod
    def inline_keyboard() -> InlineKeyboardBuilder:
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
        if self.i18n is None:
            if kwargs:
                return text.format(**kwargs)
            return text

        translated = self.i18n.gettext(text, locale=self.locale)

        if kwargs:
            return translated.format(**kwargs)

        return translated
