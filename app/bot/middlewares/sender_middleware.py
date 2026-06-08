from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from app.bot.core.file_formatting import FileFormatting
from app.bot.core.sender import Sender


class SenderMiddleware(BaseMiddleware):
    def __init__(self, formatter: FileFormatting) -> None:
        self.formatter: FileFormatting = formatter

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        data["sender"] = Sender(event=event, formatter=self.formatter)
        return await handler(event, data)
