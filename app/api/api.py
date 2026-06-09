import logging

from aiogram.types import Update
from fastapi import APIRouter, Header, Request, Response
from starlette.responses import HTMLResponse

from app.api.routes import routes
from app.bot.core.base import TelegramBot
from app.core.config import settings
from app.core.state import ApplicationState, get_app_state
from app.database.unit_of_work import UnitOfWork
from app.infrastructure.fingerprint.html_text import HTML_TEXT
from app.infrastructure.fingerprint.schemas import Payload
from app.infrastructure.payments.container import Payments
from app.infrastructure.payments.providers.core.enums import PaymentProviderName
from app.services.fingerprint_service import FingerprintService
from app.services.payment_service import PaymentService

router = APIRouter(prefix=routes.api, tags=["api"])

logger = logging.getLogger(__name__)


@router.post(path=routes.bot_webhook)
async def post_webhook_bot(request: Request):
    state: ApplicationState = request.app.state.app_state

    bot: TelegramBot = state.bot

    if bot.secret_token is not None:
        secret_token = request.headers.get("X-Telegram-Bot-Api-Secret-Token")
        if secret_token != bot.secret_token:
            return Response(status_code=403, content="Forbidden")

    update_data = await request.json()

    update = Update.model_validate(
        update_data,
        context={"bot": state.bot},
    )

    await state.dispatcher.feed_update(state.bot, update)

    return {"status": "ok"}


@router.post(path=routes.payment)
async def payment_webhook(provider_name: PaymentProviderName, request: Request):
    state: ApplicationState = get_app_state(request)

    payments: Payments | None = state.payments

    if payments is None:
        return {"status": "payments_disabled"}

    provider = payments.get(provider_name)
    if provider is None:
        return {"status": "unknown_provider"}

    payment_payload = await provider.check_invoice(request)
    if payment_payload is None:
        return {"status": "ignored"}

    if state.session_factory is None:
        return {"status": "session_factory_not_set"}

    async with UnitOfWork(
        session_factory=state.session_factory,
    ) as uow:
        service = PaymentService(uow)

        result = await service.check_paid(payment_payload.invoice_id)
        if result.success and result.user is not None and result.payment is not None:
            await uow.commit()

            await state.sender.edit_message_in_chat(
                chat_id=result.user.user_id,
                key="payment_window",
                message=state.bot.windows(locale=result.user.language).payment.payment_success(
                    amount=result.payment.amount
                ),
            )
            if settings.ADMIN_CHAT_ID is not None:
                await state.sender.send_message_to_chat(
                    chat_id=settings.ADMIN_CHAT_ID,
                    message=state.bot.windows.payment.payment_success_admin(
                        amount=result.payment.amount,
                        user_id=result.user.user_id,
                        username=result.user.username,
                        provider=PaymentProviderName(result.payment.provider),
                    ),
                )
            return {"status": "ok"}
        logger.warning(
            "Payment was not processed: payment_id=%d, reason=%s",
            payment_payload.invoice_id,
            result.reason,
        )
    return {"status": "ignored"}


@router.get(path=routes.webapp, response_class=HTMLResponse)
async def get_captcha(request: Request):
    """
    Handles GET requests to the '/webapp' endpoint and returns an HTML response.

    Returns:
        HTML_TEXT (str): A string containing the HTML content to be rendered.

    """
    return HTML_TEXT


@router.post("/webapp")
async def post_fingerprint(
    payload: Payload,
    request: Request,
    x_telegram_init_data: str | None = Header(default=None),
):
    fingerprint_service = FingerprintService(x_telegram_init_data, payload, request)
    await fingerprint_service.handle()
    return {"status": "ok"}
