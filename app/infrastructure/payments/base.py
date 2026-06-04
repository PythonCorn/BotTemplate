import json
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import StrEnum
from typing import Any


@dataclass(slots=True)
class Invoice:
    """
    Represents an invoice with necessary payment details.

    This class is used to encapsulate information regarding an invoice,
    including its unique identifier, a URL for making payments, the
    amount due, and the type of asset associated with the transaction.

    Attributes:
    invoice_id: Unique identifier for the invoice.
    pay_url: URL where payments for the invoice can be made.
    amount: Amount due on the invoice, expressed in the appropriate currency.
    asset: Type of the asset used for the transaction (optional).
    """

    invoice_id: str | int
    pay_url: str
    amount: float | int
    asset: str | Any | None = None


class PaymentProviderName(StrEnum):
    """
    Represents the names of different payment providers.

    This enumeration is used to clearly define and manage payment provider
    names in a standardized way within the application. Each member of the
    enumeration represents a specific payment provider and its corresponding
    identifier.

    Attributes:
        cryptobot: Identifier for the Cryptobot payment provider.
    """

    cryptobot = "cryptobot"


class PaymentStatus(StrEnum):
    """
    Represents the possible statuses of a payment.

    This enumeration provides a predefined set of string constants that represent
    different states a payment can be in, such as 'created', 'pending', 'paid',
    'expired', 'canceled', and 'failed'. These statuses can be used for tracking
    the lifecycle of a payment in a payment processing system. The class inherits
    from StrEnum to ensure that the enumerated values are strings, which is
    useful for cases like serialization or working with APIs.
    """

    CREATED = "created"
    PENDING = "pending"
    PAID = "paid"
    EXPIRED = "expired"
    CANCELED = "canceled"
    FAILED = "failed"


@dataclass(slots=True)
class PaymentPayload:
    """
    Represents the payload for a payment process.

    This class is used to structure and provide the data associated with a payment
    invoice. It ensures proper formatting and manipulation when interacting with
    payment-related API or services.

    Attributes:
        invoice_id (int): The unique identifier associated with the payment invoice.

    Methods:
        to_json:
            Converts the PaymentPayload instance to its JSON representation.

    """

    invoice_id: int

    def to_json(self) -> str:
        """
        Converts the instance data to a JSON-formatted string.

        This method serializes the relevant attributes of the object into a JSON
        string representation, which can be used for data exchange or storage.

        Returns:
            str: A JSON-formatted string containing the serialized data of the
            instance.
        """
        return json.dumps({"invoice_id": self.invoice_id})


class PaymentProvider(ABC):
    """
    Represents an abstract base class for payment providers.

    This class serves as a blueprint for implementing payment provider integrations. It
    defines the structure and required methods that any specific payment provider class
    must implement. The purpose of this class is to standardize how invoices are created,
    checked, and closed across different payment services to ensure consistent behavior
    and integration patterns.

    Attributes:
        is_work: A boolean attribute indicating if the payment provider is operational.
        name_provider: An instance of PaymentProviderName representing the name and type
            of the payment provider.
    """

    is_work: bool = True
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
