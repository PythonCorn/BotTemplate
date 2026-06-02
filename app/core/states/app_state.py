from dataclasses import dataclass

from aiogram import Bot, Dispatcher
from redis.asyncio import Redis


@dataclass(slots=True)
class AppState:
    bot: Bot
    dp: Dispatcher
    redis: Redis