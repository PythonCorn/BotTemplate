from aiogram.types import TelegramObject
from aiogram.utils.i18n import I18nMiddleware
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.bot.middlewares.user_middleware import TelegramUser
from app.database.cruds.get_user_language import get_user_language


class LanguageMiddleware(I18nMiddleware):
    async def get_locale(self, event: TelegramObject, data: dict) -> str:
        user: TelegramUser | None = data.get("telegram_user")
        if user is None:
            return "ru"

        session_factory: async_sessionmaker[AsyncSession] | None = data.get("session_factory")

        fallback_locale = user.language_code or "ru"

        if session_factory is None:
            return fallback_locale

        user_language = await get_user_language(
            user_id=user.id,
            session_factory=session_factory,
        )

        return user_language or fallback_locale
