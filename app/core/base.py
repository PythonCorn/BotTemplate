import logging
from collections.abc import AsyncIterator, Callable
from contextlib import AbstractAsyncContextManager, asynccontextmanager

from fastapi import FastAPI

from app.bot.core.base import TelegramBot
from app.core.logger import setup_logging
from app.core.state import AppState
from app.infrastructure.payments.providers.core.container import PaymentContainer


class BaseApp(FastAPI):
    def __init__(
        self,
        app_state: AppState | None = None,
        public_url: str | None = None,
        title: str = "Bot Template",
        debug: bool = False,
        openapi_url: str | None = None,
        swagger_ui_oauth2_redirect_url: str | None = None,
        lifespan: Callable[[FastAPI], AbstractAsyncContextManager[None]] | None = None,
        logger_level: str = "INFO",
        json_logs: bool = False,
    ):
        self._app_state: AppState | None = app_state
        self._public_url = public_url.rstrip("/") if public_url else None
        super().__init__(
            title=title,
            lifespan=lifespan if lifespan is not None else self._lifespan,
            debug=debug,
            openapi_url=openapi_url,
            swagger_ui_oauth2_redirect_url=swagger_ui_oauth2_redirect_url,
        )

        if debug:
            logger_level = "DEBUG"
        self._logger_level = logger_level
        self._json_logs = json_logs

        self._setup_logger()
        self._logger.info("Logger is initialized")

        if self._app_state is not None:
            self.state.app_state = self._app_state

    def _setup_logger(self):
        setup_logging(level=self._logger_level, json_logs=self._json_logs)
        self._logger = logging.getLogger(__name__)
        self._logger.setLevel(self._logger_level.upper())

    @property
    def app(self) -> FastAPI:
        return self

    @property
    def app_state(self) -> AppState | None:
        return self._app_state

    @property
    def bot(self) -> TelegramBot:
        if self.app_state is None:
            raise RuntimeError("AppState is not initialized")
        return self.app_state.bot

    @asynccontextmanager
    async def _lifespan(self, app: FastAPI) -> AsyncIterator[None]:
        self._logger.info("Application startup started")
        try:
            state = getattr(app.state, "app_state", None)
            if not isinstance(state, AppState):
                raise RuntimeError("AppState is not set in the request")
            base_url = await state.bot.setup_webhook(public_url=self._public_url)
            state.base_url = base_url
            payments: PaymentContainer | None = state.payments
            if isinstance(payments, PaymentContainer):
                for payment in payments:
                    logging.info(
                        f"Payment {payment.name_provider.value} set webhook: {base_url}{payment.provider_webhook_path}"
                    )
            if state.payments is not None:
                state.bot.payment_container = state.payments
            yield
        finally:
            self._logger.info("Application shutdown started")

            state = getattr(app.state, "app_state", None)
            if isinstance(state, AppState):
                await state.shutdown()
            self._logger.info("Application shutdown finished")
