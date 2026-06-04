from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.bot.core.chat_service import ChatService
from app.bot.core.file_formatting import FileFormatting
from app.bot.windows.core.container import WindowsContainer
from app.bot.windows.core.sender import Sender
from app.database.unit_of_work import UnitOfWork
from app.infrastructure.cache.redis import RedisCache
from app.infrastructure.payments.container import PaymentContainer
from app.services.container import ServiceContainer


class ServiceMiddleware(BaseMiddleware):
    """
    ServiceMiddleware is responsible for injecting dependencies and services into the
    handler context during runtime for Telegram bot event processing.

    This middleware integrates various services, such as caching, payment handling,
    chat services, and resource management into the execution flow. It also ensures
    database consistency by utilizing a UnitOfWork instance for each handler call,
    facilitating transaction management. This class is intended to simplify service
    integration and resource management for Telegram bot handlers.
    """

    def __init__(
        self,
        async_session_factory: async_sessionmaker[AsyncSession],
        redis: RedisCache,
        payment_container: PaymentContainer,
        chat_service: ChatService,
        windows_container: WindowsContainer,
    ) -> None:
        """
        Initializes a new instance of the class with the provided dependencies.

        Args:
            async_session_factory: An async sessionmaker instance used to create
                asynchronous database sessions.
            redis: Instance of RedisCache for handling cache-related operations.
            payment_container: Instance of PaymentContainer for handling payment-related
                services and utilities.
            chat_service: Instance of ChatService for managing chat-related operations.
            windows_container: Instance of WindowsContainer for handling functionalities
                associated with windows management.
        """
        self.async_session_factory = async_session_factory
        self.redis = redis
        self.payment_container = payment_container
        self.chat_service = chat_service
        self.windows_container = windows_container
        self.formatter = FileFormatting(redis=redis.redis)

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        """
        Handles the execution of an asynchronous callable with augmented dependencies.

        The method provides a structured environment for the execution of the given
        handler by injecting various services, including services for caching, chat
        management, and payment operations, as well as setting up a UnitOfWork context.
        The callable is executed in this enriched context.

        Args:
            handler: An asynchronous callable that processes the event and its associated
                data. It takes a TelegramObject and a dictionary as inputs and returns
                an awaitable result.
            event: The event object of type TelegramObject representing the action or event
                to be processed by the handler.
            data: A dictionary to hold and pass runtime service dependencies and additional
                information required by the handler.

        Returns:
            The return value from the provided handler after processing in the enriched
            context.

        Raises:
            This method does not describe explicitly raised exceptions as they depend
            on the handler and the services involved.
        """
        async with UnitOfWork(self.async_session_factory) as uow:
            """
            Creates a UnitOfWork instance using the provided async_session_factory.
            """
            data["services"] = ServiceContainer(uow=uow)
            data["cache"] = self.redis
            data["windows"] = self.windows_container
            data["payments"] = self.payment_container
            data["chat_service"] = self.chat_service
            data["sender"] = Sender(
                event=event,
                formatter=self.formatter,
            )
            return await handler(event, data)
