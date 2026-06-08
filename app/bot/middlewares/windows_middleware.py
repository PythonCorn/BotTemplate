from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.bot.middlewares.user_middleware import TelegramUser
from app.bot.windows.core.container import WindowsContainer
from app.database.cruds.get_user_language import get_user_language


class WindowsMiddleware(BaseMiddleware):
    def __init__(self, windows_container: WindowsContainer):
        self.windows_container = windows_container

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        telegram_user: TelegramUser = data["event_from_user"]
        session_factory: async_sessionmaker[AsyncSession] | None = data.get("session_factory")

        user_language = "ru"

        if session_factory is not None:
            user_language = await get_user_language(
                user_id=telegram_user.id,
                session_factory=session_factory,
            )

        data["windows"] = self.windows_container(user_language)

        return await handler(event, data)
