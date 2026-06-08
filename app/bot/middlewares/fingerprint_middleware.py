from collections.abc import Awaitable, Callable
from typing import TYPE_CHECKING, Any

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

if TYPE_CHECKING:
    from app.bot.core.base import TelegramBot
    from app.bot.middlewares.user_middleware import TelegramUser
    from app.bot.windows.core.container import WindowsContainer
from app.database.cruds.get_user_fingerprint_marker import get_user_fingerprint_marker


class FingerprintMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        telegram_user: TelegramUser = data["event_from_user"]
        session_factory: async_sessionmaker[AsyncSession] | None = data.get("session_factory")

        is_pushed = False

        if session_factory is not None:
            is_pushed = await get_user_fingerprint_marker(
                user_id=telegram_user.id,
                session_factory=session_factory,
            )

        if is_pushed:
            return await handler(event, data)
        bot: TelegramBot = data["bot"]
        windows: WindowsContainer = data["windows"]
        return await bot.send_message_to_chat(
            chat_id=telegram_user.id,
            message=windows.fingerprint.fingerprint_message(public_url=bot.base_url),
        )
