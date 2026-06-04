import json
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import StrEnum
from typing import Any


@dataclass(slots=True)
class Invoice:
    invoice_id: str | int
    pay_url: str
    amount: float | int
    asset: str | Any | None = None


class PaymentProviderName(StrEnum):
    cryptobot = "cryptobot"


class PaymentStatus(StrEnum):
    CREATED = "created"
    PENDING = "pending"
    PAID = "paid"
    EXPIRED = "expired"
    CANCELED = "canceled"
    FAILED = "failed"


@dataclass(slots=True)
class PaymentPayload:
    invoice_id: int

    def to_json(self) -> str:
        return json.dumps({"invoice_id": self.invoice_id})


class PaymentProvider(ABC):
    is_work: bool = True
    name_provider: PaymentProviderName

    @abstractmethod
    async def create_invoice(
        self, invoice_id: int, user_id: int, amount: float | int, **kwargs
    ) -> Invoice:
        raise NotImplementedError

    @abstractmethod
    async def check_invoice(self, *args, **kwargs):
        """Method for checking the status of the invoice"""

    @abstractmethod
    async def close(self) -> None:
        raise NotImplementedError
