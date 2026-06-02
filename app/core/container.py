from dataclasses import dataclass

from aiogram import Bot, Dispatcher
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker


@dataclass(slots=True)
class Container:
    bot: Bot
    dp: Dispatcher
    redis: Redis
    session_factory: async_sessionmaker[AsyncSession]

    async def shutdown(self) -> None:
        await self.redis.aclose()
        if self.bot.session is not None:
            await self.bot.session.close()
