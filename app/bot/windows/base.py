from dataclasses import dataclass
from typing import Any

from aiogram.types import InlineKeyboardMarkup, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


@dataclass(slots=True)
class WindowMessage:
    text: str | None = None
    caption: str | None = None
    reply_markup: InlineKeyboardMarkup | ReplyKeyboardMarkup | None = None

    def as_dict(self) -> dict[str, Any]:
        return {
            key: value
            for key, value in {
                "text": self.text,
                "caption": self.caption,
                "reply_markup": self.reply_markup,
            }.items()
            if value is not None
        }


class BaseWindow:
    @staticmethod
    def get_empty_keyboard() -> InlineKeyboardBuilder:
        return InlineKeyboardBuilder()
