from aiogram.utils.i18n import I18n
from redis.asyncio import Redis
from starlette.responses import FileResponse

from app.api import api
from app.bot.core.base import TelegramBot
from app.bot.handlers import payment_handler, start_handler
from app.bot.windows.core.container import Windows
from app.core.base import App
from app.core.config import settings
from app.database.session import engine, session_factory
from app.infrastructure.payments.container import Payments
from app.infrastructure.payments.providers.cryptobot import CryptobotProvider
from app.services.container import Services

app = App(
    bot=TelegramBot(token=settings.BOT_TOKEN, drop_pending_updates=True),
    ngrok=True,
    session_factory=session_factory,
    engine=engine,
    windows=Windows(i18n=I18n(path="app/locales", default_locale="ru")),
    services=Services(),
    redis=Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.REDIS_DB),
    payments=Payments(cryptobot=CryptobotProvider(token=settings.CRYPTOBOT_TOKEN)),
)


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return FileResponse("app/static/favicon.ico")


app.include_router(router=api.router)

app.dispatcher.include_router(start_handler.router)
app.dispatcher.include_router(payment_handler.router)
