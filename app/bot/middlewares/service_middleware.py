from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.database.unit_of_work import UnitOfWork
from app.infrastructure.cache.redis import RedisCache
from app.services.container import ServiceContainer


class ServiceMiddleware(BaseMiddleware):
    def __init__(self, async_session_factory: async_sessionmaker[AsyncSession]):
        self.async_session_factory = async_session_factory

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        redis: RedisCache | None = data.get("redis")
        async with UnitOfWork(self.async_session_factory) as uow:
            data["services"] = ServiceContainer(uow, redis=redis)
            return await handler(event, data)
