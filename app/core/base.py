import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from aiogram import Dispatcher
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.utils.i18n import I18n
from fastapi import FastAPI
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from app.bot.core.base import TelegramBot
from app.bot.core.file_formatting import FileFormatting
from app.bot.core.sender import BotSender
from app.bot.middlewares.i18n_middleware import I18nMiddleware
from app.bot.middlewares.sender_middleware import SenderMiddleware
from app.bot.middlewares.service_middleware import ServiceMiddleware
from app.bot.middlewares.session_factory_middleware import SessionFactoryMiddleware
from app.bot.windows.core.container import Windows
from app.core.logger import setup_logging
from app.core.state import ApplicationState
from app.infrastructure.cache.redis import RedisCache
from app.infrastructure.payments.container import Payments
from app.ngrok.get_ngrok_url import get_ngrok_public_url
from app.services.container import Services


class App(FastAPI):
    def __init__(
        self,
        bot: TelegramBot,
        windows: Windows | None = None,
        services: Services | None = None,
        payments: Payments | None = None,
        redis: Redis | None = None,
        base_url: str | None = None,
        ngrok: bool = False,
        session_factory: async_sessionmaker[AsyncSession] | None = None,
        engine: AsyncEngine | None = None,
        logger_level: str = "INFO",
        **kwargs,
    ):
        self._logger_level = logger_level
        self.logger = self._setup_logger()

        self.base_url = base_url
        self._bot = bot
        self._redis = redis
        self._cache = RedisCache(redis=redis) if redis is not None else None
        self._ngrok = ngrok
        self._session_factory = session_factory
        self._engine = engine
        self._windows = windows
        self._services = services
        self._payments = payments

        storage = RedisStorage(redis=redis) if redis is not None else None
        self._dispatcher = Dispatcher(storage=storage)

        if session_factory is not None:
            self._include_session_factory_middleware(session_factory=session_factory)

        if windows is not None:
            self._bot.windows = windows
            if session_factory is not None:
                self._include_i18n_middleware(session_factory=session_factory)
            if redis is not None:
                self._include_sender_middleware(redis=redis)

        if services is not None and session_factory is not None:
            self._include_service_middleware(services, session_factory)

        super().__init__(
            debug=logger_level.upper() == "DEBUG",
            openapi_url=None,
            lifespan=self._lifespan,
            **kwargs,
        )

    @property
    def bot(self) -> TelegramBot:
        return self._bot

    @property
    def dispatcher(self) -> Dispatcher:
        return self._dispatcher

    @property
    def app_state(self) -> ApplicationState:
        state = self.state.app_state
        if isinstance(state, ApplicationState):
            return state
        raise RuntimeError("AppState is not set in request.app.state")

    @app_state.setter
    def app_state(self, app_state: ApplicationState):
        if not isinstance(app_state, ApplicationState):
            raise TypeError("app_state must be an instance of ApplicationState")
        self.state.app_state = app_state

    @property
    def session_factory(self) -> async_sessionmaker[AsyncSession] | None:
        return self._session_factory

    @property
    def engine(self) -> AsyncEngine | None:
        return self._engine

    @property
    def windows(self) -> Windows | None:
        return self._windows

    @property
    def cache(self) -> RedisCache | None:
        return self._cache

    @property
    def i18n(self) -> I18n | None:
        return getattr(self.windows, "i18n", None)

    @property
    def services(self) -> Services | None:
        return self._services

    @property
    def payments(self) -> Payments:
        if self._payments is None:
            raise ValueError("Payments are not set")
        return self._payments

    @asynccontextmanager
    async def _lifespan(self, app: "App") -> AsyncIterator[None]:
        self.logger.info("Application startup started")
        try:
            base_url = await self._setup_base_url()

            webhook_bot = await self.bot.setup_webhook(public_url=base_url)
            self.logger.info(f"Webhook bot: {webhook_bot}")

            app.app_state = ApplicationState(
                bot=self.bot,
                dispatcher=self.dispatcher,
                base_url=base_url,
                session_factory=self.session_factory,
                engine=self.engine,
                sender=BotSender(bot=self.bot, formatter=FileFormatting(redis=self._redis)),
                payments=self.payments,
            )

            self.bot.payments = self.payments
            if self.payments is not None:
                for payment in self.payments:
                    self.logger.info(
                        f"Payment provider: {payment.name_provider} | Path: {base_url}{payment.provider_webhook_path}"
                    )

            yield
        finally:
            self.logger.info("Application shutdown started")
            await app.app_state.shutdown()
            self.logger.info("Application shutdown finished")

    async def _setup_base_url(self) -> str:
        if self.base_url is None and not self._ngrok:
            raise RuntimeError("Base URL is not set")
        base_url = self.base_url or await get_ngrok_public_url()
        if base_url is None:
            raise RuntimeError("Base URL is not set! Set public_url or ngrok=True")
        return base_url

    def _setup_logger(self):
        setup_logging(level=self._logger_level, json_logs=False)
        logger = logging.getLogger(__name__)
        logger.setLevel(self._logger_level.upper())
        return logger

    def _include_i18n_middleware(self, session_factory: async_sessionmaker[AsyncSession]):
        self.dispatcher.update.middleware(
            I18nMiddleware(bot=self.bot, session_factory=session_factory)
        )

    def _include_session_factory_middleware(
        self, session_factory: async_sessionmaker[AsyncSession]
    ):
        self.dispatcher.update.middleware(SessionFactoryMiddleware(session_factory=session_factory))

    def _include_sender_middleware(self, redis: Redis):
        self.dispatcher.update.middleware(SenderMiddleware(formatter=FileFormatting(redis=redis)))

    def _include_service_middleware(
        self, services: Services, session_factory: async_sessionmaker[AsyncSession]
    ):
        self.dispatcher.update.middleware(
            ServiceMiddleware(services=services, session_factory=session_factory)
        )
