from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, User
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.bot.core.base import TelegramBot
from app.database.cruds.get_user_language import get_user_language


class I18nMiddleware(BaseMiddleware):
    def __init__(self, bot: TelegramBot, session_factory: async_sessionmaker[AsyncSession]):
        self.bot = bot
        self.session_factory = session_factory

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        user: User = data["event_from_user"]

        locale = await get_user_language(user_id=user.id, session_factory=self.session_factory)

        if self.bot.windows is not None:
            data["windows"] = self.bot.windows(locale=locale)

        return await handler(event, data)
