from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from app.bot.windows.core.container import WindowsContainer


class WindowsMiddleware(BaseMiddleware):
    def __init__(self, windows_container: WindowsContainer):
        self.windows_container = windows_container

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        data["windows"] = self.windows_container
        return await handler(event, data)
