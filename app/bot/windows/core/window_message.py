from dataclasses import dataclass

from aiogram.types import InlineKeyboardMarkup, ReplyKeyboardMarkup


@dataclass(slots=True)
class WindowMessage:
    text: str = ""
    caption: str = ""
    reply_markup: InlineKeyboardMarkup | ReplyKeyboardMarkup | None = None
    photo_filename: str | None = None
