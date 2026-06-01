from contextlib import asynccontextmanager
from dataclasses import dataclass

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import Update
from fastapi import FastAPI, Response, Request

from app.bot.middlewares.unit_or_work_middleware import UnitOrWorkMiddleware
from app.config import settings
from app.database.session import async_session_factory

@dataclass(slots=True)
class AppState:
    bot: Bot
    dp: Dispatcher


@asynccontextmanager
async def lifespan(app: FastAPI):
    bot = Bot(token=settings.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()

    dp.update.middleware(UnitOrWorkMiddleware(async_session_factory=async_session_factory))

    dp.include_routers()

    await bot.delete_webhook(drop_pending_updates=True)
    await bot.set_webhook(
        url=settings.TELEGRAM_WEBHOOK_URL,
        secret_token=settings.TELEGRAM_WEBHOOK_SECRET_TOKEN,
        ip_address=settings.TELEGRAM_WEBHOOK_IP_ADDRESS,
        allowed_updates=dp.resolve_used_update_types(),
        drop_pending_updates=True,
    )

    app.state.app_state = AppState(bot=bot, dp=dp)

    yield

    await bot.delete_webhook()
    if bot.session is not None:
        await bot.session.close()
app = FastAPI(lifespan=lifespan)

@app.post("/webhook/bot")
async def webhook_bot(request: Request):
    state: AppState = request.app.state.app_state

    secret_token = request.headers.get("X-Telegram-Bot-Api-Secret-Token")

    if secret_token != settings.TELEGRAM_WEBHOOK_SECRET:
        return Response(status_code=403)

    update = Update.model_validate(
        await request.json(),
        context={"bot": state.bot},
    )

    await state.dp.feed_update(state.bot, update)

    return {"ok": True}
