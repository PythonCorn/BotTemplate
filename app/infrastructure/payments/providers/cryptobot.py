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

from app.infrastructure.payments.providers.core.base import PaymentProvider
from app.infrastructure.payments.providers.core.enums import PaymentProviderName
from app.infrastructure.payments.providers.core.exceptions import (
    InvalidSignatureException,
    NotTokenException,
)
from app.infrastructure.payments.providers.core.models import Invoice, PaymentPayload

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
    name_provider: PaymentProviderName = PaymentProviderName.cryptobot

    def __init__(self, token: str | None, network: Networks = Networks.TEST_NET) -> None:
        if token is None:
            raise NotTokenException("CRYPTOBOT_TOKEN is not set")
        self.token = token
        self.provider_webhook_path: str = f"{self.base_webhook_path}{self.name_provider.value}"
        self.provider = AioCryptoPay(token=token, network=network)

    async def create_invoice(
        self,
        invoice_id: int,
        amount: float | int,
        description: str | None = None,
        paid_btn_url: str | None = None,
        user_id: int | None = None,
        **kwargs,
    ) -> Invoice:

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
            invoice_id=invoice.invoice_id, pay_url=invoice.bot_invoice_url, amount=invoice.amount
        )

    async def check_invoice(self, request: Request) -> PaymentPayload | None:
        if self.token is None:
            raise NotTokenException("CRYPTOBOT_TOKEN is not set")

        signature = request.headers.get("Crypto-Pay-Api-Signature")
        body = await request.body()
        if not signature:
            raise InvalidSignatureException("Crypto-Pay-Api-Signature is not set")

        token = sha256(self.token.encode(encoding="utf-8")).digest()

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
