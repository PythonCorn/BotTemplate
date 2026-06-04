from aiogram import Dispatcher
from redis.asyncio import Redis

from app.bot.core.chat_service import ChatService
from app.bot.middlewares.service_middleware import ServiceMiddleware
from app.bot.windows.core.container import WindowsContainer
from app.database.session import async_session_factory
from app.infrastructure.cache.redis import RedisCache
from app.infrastructure.payments import PaymentContainer


def setup_service_middleware(
    dispatcher: Dispatcher,
    redis: Redis,
    payment_container: PaymentContainer,
    chat_service: ChatService,
):
    """
    Sets up the service middleware for the provided dispatcher.

    This function integrates various services like Redis, Payment Service,
    and Chat Service into the dispatcher using a custom ServiceMiddleware.
    The added middleware ensures that the required services and dependencies
    are available for processing updates.

    Args:
        dispatcher (Dispatcher): The dispatcher instance to which the middleware
            will be added.
        redis (Redis): The Redis client instance that will be used for caching.
        payment_container (PaymentContainer): The container managing payment-related
            services and dependencies.
        chat_service (ChatService): The service handling chat-related operations.

    Returns:
        None
    """
    dispatcher.update.middleware(
        ServiceMiddleware(
            async_session_factory=async_session_factory,
            redis=RedisCache(redis=redis),
            payment_container=payment_container,
            chat_service=chat_service,
            windows_container=WindowsContainer(),
        )
    )
