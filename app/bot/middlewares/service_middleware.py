from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.database.unit_of_work import UnitOfWork
from app.services.base import BaseService


class ServiceMiddleware(BaseMiddleware):
    def __init__(
        self,
        **services: type[BaseService],
    ) -> None:
        self.services = services

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        session_factory: async_sessionmaker[AsyncSession] | None = data.get("session_factory")
        if session_factory is None:
            raise RuntimeError("Session factory is not initialized")
        async with UnitOfWork(data["session_factory"]) as uow:
            data["uow"] = uow
            for service_name, service_class in self.services.items():
                data[service_name] = service_class(uow)
            return await handler(event, data)
