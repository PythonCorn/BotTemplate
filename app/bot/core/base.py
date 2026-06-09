import logging

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.base import BaseSession
from aiogram.enums import ParseMode
from aiogram.utils.i18n import I18n

from app.api import routes
from app.bot.windows.core.container import Windows
from app.infrastructure.payments.container import Payments

logger = logging.getLogger(__name__)


class TelegramBot(Bot):
    def __init__(
        self,
        token: str,
        ip_address: str | None = None,
        max_connections: int | None = None,
        allowed_updates: list[str] | None = None,
        drop_pending_updates: bool | None = None,
        secret_token: str | None = None,
        session: BaseSession | None = None,
        default: DefaultBotProperties = DefaultBotProperties(parse_mode=ParseMode.HTML),  # noqa: B008
        **kwargs,
    ):
        super().__init__(token=token, session=session, default=default, **kwargs)
        self._webhook_path = routes.routes.bot_webhook_path
        self.ip_address = ip_address
        self.max_connections = max_connections
        self.allowed_updates = allowed_updates
        self.drop_pending_updates = drop_pending_updates
        self.secret_token = secret_token
        self.url: str | None = None
        self._windows: Windows | None = None
        self._payments: Payments | None = None
        self._public_url: str | None = None
        self._web_app_webhook_path: str = routes.routes.webapp_path

    async def setup_webhook(self, public_url: str) -> str:
        self._public_url = public_url
        if self._public_url is None:
            raise ValueError("Public URL is not set")
        self.url = f"{public_url}{self.webhook_path}"
        if self.url is None:
            raise ValueError("Webhook URL is not set")
        await self.set_webhook(
            url=self.url,
            ip_address=self.ip_address,
            max_connections=self.max_connections,
            allowed_updates=self.allowed_updates,
            drop_pending_updates=self.drop_pending_updates,
            secret_token=self.secret_token,
        )
        return self.url

    @property
    def windows(self) -> Windows:
        if self._windows is None:
            raise ValueError("Windows are not set")
        return self._windows

    @windows.setter
    def windows(self, windows: Windows):
        self._windows = windows

    @property
    def payments(self) -> Payments:
        if self._payments is None:
            raise ValueError("Payments are not set")
        return self._payments

    @payments.setter
    def payments(self, payments: Payments):
        self._payments = payments

    @property
    def public_url(self) -> str:
        if self._public_url is None:
            raise ValueError("Public URL is not set")
        return self._public_url

    @property
    def webhook_path(self) -> str:
        return self._webhook_path

    @webhook_path.setter
    def webhook_path(self, webhook_path: str):
        self._webhook_path = webhook_path

    @property
    def web_app_webhook_path(self) -> str:
        return self._web_app_webhook_path

    @web_app_webhook_path.setter
    def web_app_webhook_path(self, web_app_webhook_path: str):
        self._web_app_webhook_path = web_app_webhook_path

    @property
    def i18n(self) -> I18n | None:
        return getattr(self.windows, "i18n", None)
