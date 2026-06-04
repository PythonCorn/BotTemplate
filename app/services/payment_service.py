from decimal import Decimal

from app.database.models import Payment
from app.infrastructure.payments.base import PaymentProviderName
from app.services.base import BaseService


class PaymentService(BaseService):
    async def add_new_payment(
        self, user_id: int, provider: PaymentProviderName, amount: str
    ) -> Payment:
        decimal_amount = Decimal(amount)
        return await self.uow.payments.add_new_payment(user_id, provider, decimal_amount)
