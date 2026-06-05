from dataclasses import dataclass

from aiogram import Bot, Dispatcher
from aiogram.utils.i18n import I18n
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.infrastructure.payments.container import PaymentContainer


@dataclass(slots=True)
class Container:
    """
    Represents a container for core application dependencies.

    This class serves as a centralized point for managing dependencies in the
    application, facilitating dependency injection and ensuring easy access to
    shared resources. It provides utility methods to properly handle the
    shutdown of resources such as the Redis client and bot sessions.

    Attributes:
        bot (Bot): The Bot instance used for managing Telegram bot operations.
        dp (Dispatcher): The Dispatcher instance for handling message routing.
        redis (Redis): The Redis client instance for caching and other operations.
        session_factory (async_sessionmaker[AsyncSession]): Factory for creating
            asynchronous database sessions.
        i18n (I18n): The I18n instance for managing internationalization.
        payments (PaymentContainer | None): Optional container for payment
            handling services. Defaults to None.
    """

    bot: Bot
    dp: Dispatcher
    redis: Redis
    session_factory: async_sessionmaker[AsyncSession]
    i18n: I18n
    payments: PaymentContainer | None = None

    async def shutdown(self) -> None:
        """
        Shuts down the application components safely, closing any open connections
        related to Redis and bot's session.

        Raises:
            Exception: If the Redis connection or bot's session fails to close.

        """
        await self.redis.aclose()
        if self.bot.session is not None:
            await self.bot.session.close()
