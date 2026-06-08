from aiogram.utils.i18n import I18n
from redis.asyncio import Redis
from starlette.responses import FileResponse

from app.api import api, health, webhook
from app.bot.core.base import TelegramBot
from app.bot.handlers import payment_handler, start_handler
from app.core.base import BaseApp
from app.core.config import settings
from app.core.state import AppState
from app.database.session import async_engine, async_session_factory
from app.infrastructure.cache.redis import RedisCache
from app.infrastructure.payments.providers.core.container import PaymentContainer
from app.infrastructure.payments.providers.cryptobot import CryptobotProvider
from app.services.payment_service import PaymentService
from app.services.user_service import UserService

i18n = I18n(path="app/locales", default_locale="ru")


redis = RedisCache(
    redis=Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        db=settings.REDIS_DB,
        password=settings.REDIS_PASSWORD or None,
    )
)

bot = TelegramBot(
    token=settings.BOT_TOKEN,
    i18n=i18n,
    redis=redis,
    secret_token=settings.TELEGRAM_WEBHOOK_SECRET_TOKEN,
    session_factory=async_session_factory,
    fingerprint=True,
)

payment_container = PaymentContainer(cryptobot=CryptobotProvider(token=settings.CRYPTOBOT_TOKEN))

app = BaseApp(
    app_state=AppState(
        bot=bot,
        session_factory=async_session_factory,
        engine=async_engine,
        payments=payment_container,
    )
)


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return FileResponse("app/static/favicon.ico")


# FastApi Routers
app.include_router(router=webhook.router)
app.include_router(router=health.router)
app.include_router(router=api.router)

# Bot routers
bot.include_router(router=start_handler.router)
bot.include_router(router=payment_handler.router)

# Bot middlewares

bot.include_services(users=UserService)
bot.include_services(payments=PaymentService)
