from aiogram.types import TelegramObject, User
from aiogram.utils.i18n import I18nMiddleware

from app.services.container import ServiceContainer


class LanguageMiddleware(I18nMiddleware):
    async def get_locale(self, event: TelegramObject, data: dict) -> str:
        services: ServiceContainer | None = data.get("services")
        if services is None:
            return "ru"

        # Получаем user_id универсально
        user: User | None = data.get("event_from_user")
        if user is None:
            return "ru"

        return await services.users.get_user_language(user.id)
