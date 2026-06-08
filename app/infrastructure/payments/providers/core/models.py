import json
from dataclasses import dataclass


@dataclass(slots=True)
class Invoice:
    invoice_id: int | str
    pay_url: str
    amount: float | int


@dataclass(slots=True)
class PaymentPayload:
    invoice_id: int

    def to_json(self) -> str:
        return json.dumps({"invoice_id": self.invoice_id})
