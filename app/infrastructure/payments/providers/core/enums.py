from enum import StrEnum


class PaymentProviderName(StrEnum):
    cryptobot = "cryptobot"


class PaymentStatus(StrEnum):
    CREATED = "created"
    PAID = "paid"


class PaymentAsset(StrEnum):
    USD = "USD"
