from aiogram.types import Update
from fastapi import APIRouter, Request, Response


from app.core.config import settings
from app.core.states.app_state import AppState
from app.core.states.get_app_state import get_app_state

router = APIRouter(prefix="/webhook", tags=["webhook"])


@router.post("/bot")
async def webhook_bot(request: Request):
    state: AppState = get_app_state(request)

    secret_token = request.headers.get("X-Telegram-Bot-Api-Secret-Token")

    if secret_token != settings.TELEGRAM_WEBHOOK_SECRET:
        return Response(status_code=403)

    update = Update.model_validate(
        await request.json(),
        context={"bot": state.bot},
    )

    await state.dp.feed_update(state.bot, update)

    return {"ok": True}