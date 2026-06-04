import logging
from decimal import Decimal

from sqlalchemy import select

from app.database.models import Payment
from app.database.repositories.base import BaseRepository
from app.infrastructure.payments.base import PaymentProviderName

logger = logging.getLogger(__name__)


class PaymentRepository(BaseRepository[Payment]):
    async def add_new_payment(
        self, user_id: int, provider: PaymentProviderName, amount: Decimal
    ) -> Payment:
        model = Payment(user_id=user_id, provider=provider, amount=amount)
        self.session.add(model)
        await self.session.flush()
        return model

    async def get_for_update(self, payment_id: int) -> Payment | None:
        stmt = select(Payment).where(Payment.id == payment_id).with_for_update(skip_locked=True)
        result = await self.session.scalar(stmt)
        logger.info(f"Payment {result}")
        return result
