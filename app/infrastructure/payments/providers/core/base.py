from abc import ABC, abstractmethod
from typing import ClassVar

from app.infrastructure.payments.providers.core.enums import PaymentProviderName
from app.infrastructure.payments.providers.core.models import Invoice, PaymentPayload


class PaymentProvider(ABC):
    base_webhook_path: ClassVar[str] = "/webhook/payment/"
    provider_webhook_path: str
    name_provider: PaymentProviderName

    @abstractmethod
    async def create_invoice(self, *args, **kwargs) -> Invoice:
        """Method for creating a new invoice"""
        raise NotImplementedError

    @abstractmethod
    async def check_invoice(self, *args, **kwargs) -> PaymentPayload | None:
        """Method for checking the status of the invoice"""
        raise NotImplementedError

    @abstractmethod
    async def close(self) -> None:
        """Method for closing the payment provider"""
        raise NotImplementedError
