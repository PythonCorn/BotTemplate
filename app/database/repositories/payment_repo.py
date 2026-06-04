from decimal import Decimal

from app.database.models import Payment
from app.database.repositories.base import BaseRepository
from app.infrastructure.payments.base import PaymentProviderName


class PaymentRepository(BaseRepository[Payment]):
    async def add_new_payment(
        self, user_id: int, provider: PaymentProviderName, amount: Decimal
    ) -> Payment:
        model = Payment(user_id=user_id, provider=provider, amount=amount)
        self.session.add(model)
        await self.session.flush()
        return model
