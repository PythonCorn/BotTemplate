import logging

from aiogram.types import Update
from fastapi import APIRouter, Request, Response

from app.core.app_state import AppState, get_app_state
from app.core.config import settings
from app.infrastructure.payments.base import PaymentPayload
from app.infrastructure.payments.container import PaymentContainer
from app.infrastructure.payments.cryptobot_provider import CryptobotProvider

router = APIRouter(prefix="/webhook", tags=["webhook"])

logger = logging.getLogger(__name__)


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


@router.post("/payment/cryptobot")
async def get_webhook_cryptobot(request: Request):
    state: AppState = get_app_state(request)
    payment_container: PaymentContainer | None = state.container.payments
    if payment_container is not None and isinstance(payment_container.cryptobot, CryptobotProvider):
        cryptobot: CryptobotProvider = payment_container.cryptobot
        payment_payload: PaymentPayload | None = await cryptobot.check_invoice(request)
        logger.info(f"Payment payload: {payment_payload}")
    return {"status": "ok"}
