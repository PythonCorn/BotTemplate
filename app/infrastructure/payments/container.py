from collections.abc import Iterator
from dataclasses import dataclass, fields

from app.infrastructure.payments.base import PaymentProvider, PaymentProviderName
from app.infrastructure.payments.cryptobot_provider import CryptobotProvider


@dataclass(slots=True)
class PaymentContainer:
    """
    PaymentContainer class.

    A container class for handling multiple payment providers. Provides mechanisms
    to iterate over the available providers, retrieve a specific provider by name,
    and close all providers asynchronously.

    Attributes:
        cryptobot (CryptobotProvider | None): An optional payment provider.

    Methods:
        __iter__(): Returns an iterator over the non-None payment providers in the
        container.

        close(): Asynchronously closes all payment providers in the container.

        get(name: PaymentProviderName): Retrieves a payment provider based on its name.
    """

    cryptobot: CryptobotProvider | None = None

    def __iter__(self) -> Iterator[PaymentProvider]:
        """
        Iterates over non-None payment providers available in the object.

        Yields:
            Iterator[PaymentProvider]: An iterator over payment providers that are
            not None.
        """
        for field in fields(self):
            provider = getattr(self, field.name)
            if provider is not None:
                yield provider

    async def close(self) -> None:
        """
        Closes all providers asynchronously.

        This method iterates through all providers in the collection and calls their
        `close` method asynchronously to release any resources they might be using.

        Raises:
            Any exceptions raised by the `close` methods of individual providers.
        """
        for provider in self:
            await provider.close()

    def get(self, name: PaymentProviderName | str) -> PaymentProvider | None:
        """
        Retrieves a payment provider by its name.

        Searches for a payment provider within the current object using the
        provided PaymentProviderName enumeration value. If no matching payment
        provider is found, returns None.

        Parameters:
        name: PaymentProviderName
            The name of the payment provider to retrieve.

        Returns:
        PaymentProvider | None
            The payment provider object if found, otherwise None.
        """
        provider: PaymentProvider | None = getattr(
            self,
            name.value if isinstance(name, PaymentProviderName) else name,
        )
        return provider
