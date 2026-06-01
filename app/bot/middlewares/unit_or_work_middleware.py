from typing import Callable, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from app.database.unit_of_work import UnitOfWork


class UnitOrWorkMiddleware(BaseMiddleware):
    def __init__(self, async_session_factory: async_sessionmaker[AsyncSession]):
        self.async_session_factory = async_session_factory

    async def __call__(
            self,
            handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: dict[str, Any],
    ) -> Any:
        async with UnitOfWork(self.async_session_factory) as uow:
            data["uow"] = uow
            return await handler(event, data)
