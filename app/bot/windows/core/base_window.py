from aiogram.types import InlineKeyboardMarkup, ReplyKeyboardMarkup
from aiogram.utils.i18n import I18n
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.bot.windows.core.window_message import WindowMessage
from app.database.cruds.get_user_language import get_user_language


class BaseWindow:
    def __init__(self, i18n: I18n | None = None, locale: str = "ru") -> None:
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
        translated = text if self.i18n is None else self.i18n.gettext(text, locale=self.locale)

        if kwargs:
            return translated.format(**kwargs)

        return translated

    @classmethod
    async def set_locale(cls, i18n: I18n, user_id: int, session_factory) -> "BaseWindow":
        locale = await get_user_language(user_id, session_factory)
        return cls(i18n=i18n, locale=locale)
