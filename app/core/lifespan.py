from contextlib import asynccontextmanager

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisStorage
from fastapi import FastAPI
from redis.asyncio import Redis

from app.bot.middlewares.redis_middleware import RedisMiddleware
from app.bot.middlewares.unit_or_work_middleware import UnitOrWorkMiddleware
from app.core.cache.redis import RedisCache
from app.core.config import settings
from app.core.states.app_state import AppState
from app.database.session import async_session_factory


@asynccontextmanager
async def lifespan(app: FastAPI):
    redis = Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        db=settings.REDIS_DB,
        password=settings.REDIS_PASSWORD
    )
    redis_cache = RedisCache(redis=redis)
    bot = Bot(token=settings.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    storage = RedisStorage(redis=redis, state_ttl=60 * 60 * 2)

    dp = Dispatcher(storage=storage)

    dp.update.middleware(UnitOrWorkMiddleware(async_session_factory=async_session_factory))
    dp.update.middleware(RedisMiddleware(redis=redis_cache))

    dp.include_routers()

    await bot.delete_webhook(drop_pending_updates=True)
    await bot.set_webhook(
        url=settings.TELEGRAM_WEBHOOK_URL,
        secret_token=settings.TELEGRAM_WEBHOOK_SECRET_TOKEN,
        ip_address=settings.TELEGRAM_WEBHOOK_IP_ADDRESS,
        allowed_updates=dp.resolve_used_update_types(),
        drop_pending_updates=True,
    )

    app.state.app_state = AppState(bot=bot, dp=dp, redis=redis)
    
    try:
        yield
    finally:
        await bot.delete_webhook()
        if bot.session is not None:
            await bot.session.close()
        await storage.close()
