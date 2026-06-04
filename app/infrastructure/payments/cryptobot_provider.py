import hashlib
import hmac
import json
from hashlib import sha256

import orjson
from aiocryptopay import AioCryptoPay, Networks
from aiocryptopay.const import Assets, InvoiceStatus, PaidButtons
from aiocryptopay.models.invoice import Invoice as CryptobotInvoice
from aiocryptopay.models.update import Update
from fastapi import Request

from app.core.config import settings
from app.infrastructure.payments.base import (
    Invoice,
    PaymentPayload,
    PaymentProvider,
    PaymentProviderName,
)

ACCEPTED_ASSETS = [
    Assets.USDT,
    Assets.TON,
    Assets.BTC,
    Assets.LTC,
    Assets.ETH,
    Assets.BNB,
    Assets.TRX,
    Assets.USDC,
]


class CryptobotProvider(PaymentProvider):
    """
    A provider class for interacting with the CryptoBot payment service.

    This class extends PaymentProvider and provides functionality to create
    payment invoices, verify incoming payments from requests, and manage the
    connection lifecycle with CryptoBot services. It is specialized for use
    with the CryptoBot API, handling fiat-to-crypto payment flows. The class
    is initialized with an optional API token, and if no token is provided,
    the provider is set to an inactive state.

    Attributes:
        name_provider (PaymentProviderName): The name of the payment provider,
            set to `PaymentProviderName.cryptobot`.

    Methods:
        __init__(token: str | None): Initializes the provider with an optional
            API token. If none is provided, it sets the provider to an inactive
            state.
        create_invoice(invoice_id: int, user_id: int, amount: float | int,
            description: str | None, paid_btn_url: str | None, **kwargs) ->
            Invoice: Asynchronously creates a payment invoice using the CryptoBot
            API.
        check_invoice(request: Request) -> PaymentPayload | None: Asynchronously
            verifies and processes an incoming payment request, returning a parsed
            PaymentPayload if valid.
        close() -> None: Asynchronously closes the connection and resources used
            by the provider instance.
    """

    name_provider: PaymentProviderName = PaymentProviderName.cryptobot

    def __init__(self, token: str | None = None) -> None:
        """
        Represents an initialization method for the class.

        Attributes:
        token (str | None): The token provided to authenticate with the AioCryptoPay
            service. If None, the instance will not be operational.
        is_work (bool): Indicates whether the instance is operational. Defaults to
            False if no token is provided.
        provider (AioCryptoPay): An instance of AioCryptoPay configured with the
            provided token and operating on the MAIN_NET network.

        Parameters:
        token: A string representing the token for authentication, or None if no token
            is provided.

        Returns:
        None
        """
        self.token = token
        if self.token is None:
            self.is_work = False
            return
        self.provider = AioCryptoPay(token=self.token, network=Networks.TEST_NET)

    async def create_invoice(
        self,
        invoice_id: int,
        amount: float | int,
        description: str | None = None,
        paid_btn_url: str | None = None,
        user_id: int | None = None,
        **kwargs,
    ) -> Invoice:
        """
        Creates an invoice using the payment provider and returns the generated invoice object.

        This method utilizes an external payment provider to create an invoice based on the
        parameters provided. The created invoice can include optional descriptive text and
        a paid button URL. The method ensures that the amount is processed as a float and
        sets payment-related configurations like the accepted assets and currencies.

        Arguments:
            invoice_id (int): The unique identifier for the invoice.
            user_id (int): The unique identifier for the user associated with the invoice.
            amount (float | int): The invoice amount. It is processed as a float internally.
            description (str | None, optional): A description of the invoice. Defaults to None.
            paid_btn_url (str | None, optional): A URL associated with the payment button.
                If specified, creates a paid button in the external payment provider. Defaults to None.
            **kwargs: Additional parameters that may be required by the payment provider.

        Returns:
            Invoice: An object representing the invoice, including its payment URL, amount,
            and associated asset.
        """
        paid_btn_name = PaidButtons.OPEN_BOT if paid_btn_url is not None else None
        invoice: CryptobotInvoice = await self.provider.create_invoice(
            amount=float(amount),
            description=description,
            payload=PaymentPayload(invoice_id=invoice_id).to_json(),
            fiat="USD",
            swap_to="USDT",
            paid_btn_name=paid_btn_name,
            paid_btn_url=paid_btn_url,
            currency_type="fiat",
            accepted_assets=ACCEPTED_ASSETS,
        )
        return Invoice(
            invoice_id=invoice.invoice_id,
            pay_url=invoice.bot_invoice_url,
            amount=invoice.amount,
            asset=invoice.asset,
        )

    async def check_invoice(self, request: Request) -> PaymentPayload | None:
        """
        Validates and processes a payment invoice received from the Cryptobot API.

        This asynchronous method verifies the Cryptobot invoice by checking the API signature, decoding the payload, and ensuring
        its authenticity. If the invoice status is marked as 'PAID' and the payload is valid, it returns a `PaymentPayload`
        object representing the payment details. Otherwise, it returns None.

        Args:
            request (Request): The HTTP request containing the invoice data and headers
                sent from the Cryptobot API.

        Returns:
            PaymentPayload | None: A `PaymentPayload` object with the payment details if
                the invoice is paid and valid. Returns None if the Cryptobot token is
                not set, the signature is absent or invalid, or if the invoice status
                and payload are not compliant.

        Raises:
            None
        """
        if settings.CRYPTOBOT_TOKEN is None:
            return None

        signature = request.headers.get("Crypto-Pay-Api-Signature")
        body = await request.body()
        if not signature:
            return None

        token = sha256(settings.CRYPTOBOT_TOKEN.encode(encoding="utf-8")).digest()

        check_signature = hmac.new(
            token,
            body,
            hashlib.sha256,
        ).hexdigest()

        if not hmac.compare_digest(check_signature, signature):
            return None

        data = orjson.loads(body)

        update: Update = Update.model_validate(data)
        cryptobot_payload: CryptobotInvoice = update.payload
        payment_payload: str | None = cryptobot_payload.payload
        status: InvoiceStatus | str = cryptobot_payload.status

        if status == InvoiceStatus.PAID and isinstance(payment_payload, str):
            data = json.loads(payment_payload)
            return PaymentPayload(**data)
        return None

    async def close(self) -> None:
        await self.provider.close()
