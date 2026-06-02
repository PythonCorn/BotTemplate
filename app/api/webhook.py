from aiogram.types import Update
from fastapi import APIRouter, Request, Response

from app.core.app_state import AppState, get_app_state
from app.core.config import settings

router = APIRouter(prefix="/webhook", tags=["webhook"])


@router.post("/bot")
async def webhook_bot(request: Request):
    state: AppState = get_app_state(request)

    secret_token = request.headers.get("X-Telegram-Bot-Api-Secret-Token")

    if secret_token != settings.TELEGRAM_WEBHOOK_SECRET_TOKEN:
        return Response(status_code=403)

    update_data = await request.json()

    update = Update.model_validate(
        update_data,
        context={"bot": state.container.bot},
    )

    await state.container.dp.feed_update(state.container.bot, update)

    return {"ok": True}
