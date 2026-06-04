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
    name_provider: PaymentProviderName = PaymentProviderName.cryptobot

    def __init__(self, token: str | None = None):
        self.token = token
        if self.token is None:
            self.is_work = False
            return
        self.provider = AioCryptoPay(token=self.token, network=Networks.MAIN_NET)

    async def create_invoice(
        self,
        invoice_id: int,
        user_id: int,
        amount: float | int,
        description: str | None = None,
        paid_btn_url: str | None = None,
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
            invoice_id=invoice.invoice_id,
            pay_url=invoice.bot_invoice_url,
            amount=invoice.amount,
            asset=invoice.asset,
        )

    async def check_invoice(self, request: Request) -> PaymentPayload | None:
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
