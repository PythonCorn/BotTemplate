from dataclasses import dataclass

from app.infrastructure.payments.providers.core.base_container import BaseContainer
from app.infrastructure.payments.providers.cryptobot import CryptobotProvider


@dataclass(slots=True)
class PaymentContainer(BaseContainer):
    cryptobot: CryptobotProvider

    notify_admins: bool = True
