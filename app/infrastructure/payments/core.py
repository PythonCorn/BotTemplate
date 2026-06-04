from app.infrastructure.payments.container import PaymentContainer
from app.infrastructure.payments.cryptobot_provider import CryptobotProvider


def create_payment_container(cryptobot_provider: CryptobotProvider | None = None):
    """
    Функция для добавления платежных провайдеров!
    """
    return PaymentContainer(cryptobot=cryptobot_provider)


__all__ = ["create_payment_container"]
