import logging
from decimal import Decimal

from aiogram.types import Update
from fastapi import APIRouter, Request, Response

from app.bot.windows.core.notifier import PaymentSuccessNotifier
from app.core.app_state import AppState, get_app_state
from app.core.config import settings
from app.database.unit_of_work import UnitOfWork
from app.infrastructure.payments.base import PaymentProvider, PaymentProviderName
from app.infrastructure.payments.container import PaymentContainer
from app.services.payment_service import PaymentService

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


@router.post("/payment/{provider_name}")
async def payment_webhook(provider_name: PaymentProviderName, request: Request):
    state: AppState = get_app_state(request)

    payments: PaymentContainer | None = state.container.payments
    if payments is None:
        return {"status": "payments_disabled"}

    provider: PaymentProvider | None = payments.get(provider_name)
    if provider is None:
        return {"status": "unknown_provider"}

    payment_payload = await provider.check_invoice(request)
    if payment_payload is None:
        return {"status": "ignored"}

    async with UnitOfWork(
        async_session_factory=state.container.session_factory,
    ) as uow:
        service = PaymentService(uow)
        result = await service.paid(payment_payload.invoice_id)

        if result.success and result.user is not None and result.payment is not None:
            await uow.commit()
            notifier = PaymentSuccessNotifier(bot=state.container.bot, i18n=state.container.i18n)
            if settings.ADMIN_CHAT_ID is not None:
                await notifier.notify_admin(
                    user_id=result.user.user_id,
                    username=result.user.username or str(result.user.user_id),
                    amount=result.payment.amount,
                    provider=provider_name,
                    admin_chat_id=settings.ADMIN_CHAT_ID,
                )
            await notifier.notify_user(
                user_id=result.user.user_id,
                amount=result.payment.amount,
                locale=result.user.language,
            )
            logger.info(
                "Payment processed: payment_id=%d, user_id=%d, amount=%s",
                result.payment.id,
                result.user.user_id,
                result.payment.amount.quantize(Decimal("0.01")),
            )

            return {"status": "ok"}

        logger.warning(
            "Payment was not processed: payment_id=%d, reason=%s",
            payment_payload.invoice_id,
            result.reason,
        )

    return {
        "status": "ignored",
        "reason": result.reason,
    }
