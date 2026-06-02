import logging
from contextlib import asynccontextmanager

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisStorage
from fastapi import FastAPI
from redis.asyncio import Redis

from app.bot.core.setup_bot_routers import setup_bot_routers
from app.bot.middlewares.redis_middleware import RedisMiddleware
from app.bot.middlewares.unit_of_work_middleware import UnitOfWorkMiddleware
from app.core.cache.redis import RedisCache
from app.core.config import settings
from app.core.states.app_state import AppState
from app.database.session import async_engine, async_session_factory
from app.ngrok.get_ngrok_url import get_ngrok_public_url

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Application startup started")

    redis = Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        db=settings.REDIS_DB,
        password=settings.REDIS_PASSWORD or None,
    )
    redis_cache = RedisCache(redis=redis)
    bot = Bot(token=settings.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    storage = RedisStorage(redis=redis, state_ttl=60 * 60 * 2)

    dp = Dispatcher(storage=storage)

    dp.update.middleware(UnitOfWorkMiddleware(async_session_factory=async_session_factory))
    dp.update.middleware(RedisMiddleware(redis=redis_cache))

    setup_bot_routers(dispatcher=dp)

    public_url = settings.PUBLIC_URL or await get_ngrok_public_url()

    if not public_url:
        raise RuntimeError("Public URL is not set")

    bot_webhook_url = f"{public_url}/{settings.TELEGRAM_WEBHOOK_URL}"

    await bot.delete_webhook(drop_pending_updates=True)
    await bot.set_webhook(
        url=bot_webhook_url,
        secret_token=settings.TELEGRAM_WEBHOOK_SECRET_TOKEN,
        ip_address=settings.TELEGRAM_WEBHOOK_IP_ADDRESS or None,
        allowed_updates=dp.resolve_used_update_types(),
        drop_pending_updates=True,
    )

    logger.info("Telegram webhook configured: %s", bot_webhook_url)

    app.state.app_state = AppState(bot=bot, dp=dp, redis=redis)

    try:
        logger.info("Application startup completed")
        yield
    finally:
        logger.info("Application shutdown started")
        await bot.delete_webhook()
        if bot.session is not None:
            await bot.session.close()
        await storage.close()
        await redis.aclose()
        await async_engine.dispose()
        logger.info("Application shutdown completed")
