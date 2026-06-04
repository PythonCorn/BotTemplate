from aiogram import Dispatcher
from redis.asyncio import Redis

from app.bot.core.chat_service import ChatService
from app.bot.middlewares.service_middleware import ServiceMiddleware
from app.bot.windows.container import WindowsContainer
from app.database.session import async_session_factory
from app.infrastructure.cache.redis import RedisCache
from app.infrastructure.payments import PaymentContainer


def setup_service_middleware(
    dispatcher: Dispatcher,
    redis: Redis,
    payment_container: PaymentContainer,
    chat_service: ChatService,
):
    dispatcher.update.middleware(
        ServiceMiddleware(
            async_session_factory=async_session_factory,
            redis=RedisCache(redis=redis),
            payment_container=payment_container,
            chat_service=chat_service,
            windows_container=WindowsContainer(),
        )
    )
