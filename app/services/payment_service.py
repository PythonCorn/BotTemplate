import logging
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation

from app.database.models import Payment, User
from app.infrastructure.payments.providers.core.enums import PaymentProviderName, PaymentStatus
from app.infrastructure.payments.providers.core.exceptions import InvalidAmountException
from app.services.base import BaseService

logger = logging.getLogger(__name__)


@dataclass(slots=True, frozen=True)
class PaymentPaidResult:
    success: bool
    user: User | None = None
    payment: Payment | None = None
    reason: str | None = None


class PaymentService(BaseService):
    async def create_payment(self, user_id: int, amount: str, provider: PaymentProviderName | str):
        try:
            decimal_amount = Decimal(amount).quantize(Decimal("0.01"))
        except InvalidOperation as err:
            raise InvalidAmountException(f"Invalid payment amount: {amount}") from err

        payment: Payment = await self.uow.payments.add_new_payment(
            user_id=user_id,
            provider=provider,
            amount=decimal_amount,
        )
        logger.info(f"Payment created: {payment}")
        await self.uow.flush()
        return payment

    async def paid(self, payment_id: int) -> PaymentPaidResult:
        payment = await self.uow.payments.get_for_update(payment_id)

        if payment is None:
            return PaymentPaidResult(
                success=False,
                reason="payment_not_found",
            )

        if payment.status != PaymentStatus.CREATED:
            return PaymentPaidResult(
                success=False,
                payment=payment,
                reason="payment_already_processed",
            )

        user: User | None = await self.uow.users.get_for_update(payment.user_id)

        if user is None:
            logger.error(
                "User %d not found for payment %d",
                payment.user_id,
                payment.id,
            )
            return PaymentPaidResult(
                success=False,
                payment=payment,
                reason="user_not_found",
            )

        payment.status = PaymentStatus.PAID
        user.balance += payment.amount

        logger.info(
            "User %d paid %s for %s",
            user.user_id,
            payment.amount,
            payment.provider,
        )
        logger.info(
            "User %d balance is now %s",
            user.user_id,
            user.balance,
        )

        return PaymentPaidResult(
            success=True,
            user=user,
            payment=payment,
        )
