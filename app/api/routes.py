from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Routes:
    api: str = "/api"
    bot_webhook: str = "/webhook/bot"
    webapp: str = "/webapp"
    payment: str = "/payment/{provider_name}"

    @property
    def bot_webhook_path(self) -> str:
        return f"{self.api}{self.bot_webhook}"

    @property
    def webapp_path(self) -> str:
        return f"{self.api}{self.webapp}"

    @property
    def payment_path(self) -> str:
        return f"{self.api}{self.payment}"


routes = Routes()
