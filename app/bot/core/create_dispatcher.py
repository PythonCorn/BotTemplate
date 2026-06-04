from aiogram import Dispatcher
from aiogram.fsm.storage.redis import RedisStorage
from redis.asyncio import Redis


def create_dispatcher(redis: Redis) -> Dispatcher:
    storage = RedisStorage(redis=redis, state_ttl=60 * 60 * 2)
    return Dispatcher(storage=storage)
