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


@dataclass(slots=True)
class PaymentPayload:
    user_id: int
    amount: float | int

    def to_json(self) -> str:
        return json.dumps({"user_id": self.user_id, "amount": self.amount})


class PaymentName(StrEnum):
    cryptobot = "cryptobot"


class PaymentProvider(ABC):
    is_work: bool = True
    name_provider: PaymentName

    @abstractmethod
    async def create_invoice(self, user_id: int, amount: float | int, **kwargs) -> Invoice:
        raise NotImplementedError

    @abstractmethod
    async def close(self) -> None:
        raise NotImplementedError
