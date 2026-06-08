import logging
from decimal import Decimal

from sqlalchemy import delete, select

from app.database.models import Payment
from app.database.repositories.base import BaseRepository
from app.infrastructure.payments.providers.core.enums import PaymentProviderName

logger = logging.getLogger(__name__)


class PaymentRepository(BaseRepository[Payment]):
    async def add_new_payment(
        self, user_id: int, provider_name: PaymentProviderName | str, amount: Decimal
    ) -> Payment:
        model = Payment(user_id=user_id, provider=PaymentProviderName(provider_name), amount=amount)
        self.session.add(model)
        await self.session.flush()
        return model

    async def get_for_update(self, payment_id: int) -> Payment | None:
        stmt = select(Payment).where(Payment.id == payment_id).with_for_update(skip_locked=True)
        result = await self.session.scalar(stmt)
        logger.info(f"Payment {result}")
        return result

    async def clear_table(self):
        stmt = delete(Payment)
        await self.session.execute(stmt)
