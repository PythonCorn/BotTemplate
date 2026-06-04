import logging
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation

from app.database.models import Payment, User
from app.infrastructure.payments.base import PaymentProviderName, PaymentStatus
from app.services.base import BaseService

logger = logging.getLogger(__name__)


@dataclass(slots=True, frozen=True)
class PaymentPaidResult:
    success: bool
    user: User | None = None
    payment: Payment | None = None
    reason: str | None = None


class PaymentService(BaseService):
    async def add_new_payment(
        self,
        user_id: int,
        provider: PaymentProviderName,
        amount: str,
    ) -> Payment:
        """
        Adds a new payment record for a specified user with the given payment provider
        and amount.

        This method validates the provided payment amount and creates a payment
        entry in the database through the unit of work.

        Parameters:
        user_id: int
            The unique identifier of the user making the payment.
        provider: PaymentProviderName
            The payment provider through which the payment is processed.
        amount: str
            The payment amount to be processed. Must be convertible to a valid
            decimal.

        Returns:
        Payment
            Returns the created Payment object containing the information of the
            newly created payment record.

        Raises:
        ValueError
            Raised when the provided amount cannot be converted into a decimal.
        """
        try:
            decimal_amount = Decimal(amount)
        except InvalidOperation:
            raise ValueError(f"Invalid payment amount: {amount}")  # noqa: B904

        result = await self.uow.payments.add_new_payment(
            user_id=user_id,
            provider=provider,
            amount=decimal_amount,
        )
        await self.uow.commit()
        return result

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
