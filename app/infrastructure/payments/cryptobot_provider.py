from aiocryptopay import AioCryptoPay, Networks
from aiocryptopay.const import Assets, PaidButtons
from aiocryptopay.models.invoice import Invoice as CryptobotInvoice

from app.infrastructure.payments.base import Invoice, PaymentName, PaymentPayload, PaymentProvider

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
    def __init__(self, token: str | None = None):
        self.token = token
        if self.token is None:
            self.is_work = False
            return
        self.name_provider: PaymentName = PaymentName.cryptobot
        self.provider = AioCryptoPay(token=self.token, network=Networks.MAIN_NET)

    async def create_invoice(
        self, user_id: int, amount: float | int, paid_btn_url: str | None = None, **kwargs
    ) -> Invoice:
        paid_btn_name = PaidButtons.OPEN_BOT if paid_btn_url is not None else None
        invoice: CryptobotInvoice = await self.provider.create_invoice(
            amount=float(amount),
            description="Purchase of mobile proxies",
            payload=PaymentPayload(user_id=user_id, amount=amount).to_json(),
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

    async def close(self) -> None:
        await self.provider.close()
