from collections.abc import Iterator
from dataclasses import dataclass, fields

from app.infrastructure.payments.base import PaymentProvider
from app.infrastructure.payments.cryptobot_provider import CryptobotProvider


@dataclass(slots=True)
class PaymentContainer:
    cryptobot: CryptobotProvider | None = None

    def __iter__(self) -> Iterator[PaymentProvider]:
        for field in fields(self):
            provider = getattr(self, field.name)
            if provider is not None:
                yield provider

    async def close(self) -> None:
        for provider in self:
            if provider is not None:
                await provider.close()
