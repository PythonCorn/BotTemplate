import logging
from datetime import datetime, timedelta
from typing import Literal

from aiogram import BaseMiddleware, Bot, Dispatcher, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ChatMemberStatus, ParseMode
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.utils.i18n import I18n
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.bot.core.file_formatting import FileFormatting
from app.bot.core.setup_i18n import ConfigI18n, get_i18n
from app.bot.middlewares.language_middleware import LanguageMiddleware
from app.bot.middlewares.sender_middleware import SenderMiddleware
from app.bot.middlewares.service_middleware import ServiceMiddleware
from app.bot.middlewares.session_factory_middleware import SessionFactoryMiddleware
from app.bot.middlewares.user_middleware import UserMiddleware
from app.bot.middlewares.windows_middleware import WindowsMiddleware
from app.bot.windows.core.base_window import BaseWindow
from app.bot.windows.core.container import WindowsContainer
from app.bot.windows.core.window_message import WindowMessage
from app.database.cruds.get_user_language import get_user_language
from app.infrastructure.cache.redis import RedisCache
from app.infrastructure.payments.providers.core.container import PaymentContainer
from app.ngrok.get_ngrok_url import get_ngrok_public_url
from app.services.base import BaseService

logger = logging.getLogger(__name__)


class TelegramBot(Bot):
    def __init__(
        self,
        token: str,
        session_factory: async_sessionmaker[AsyncSession],
        secret_token: str | None = None,
        ip_address: str | None = None,
        allowed_updates: list[str] | None = None,
        parse_mode: ParseMode = ParseMode.HTML,
        config_i18n: ConfigI18n | None = None,
        redis: RedisCache | None = None,
        webhook_path: str = "/webhook/bot",
    ):
        super().__init__(token=token, default=DefaultBotProperties(parse_mode=parse_mode))

        self._session_factory = session_factory
        self._redis = redis
        self._dispatcher = Dispatcher(storage=self._setup_redis())
        self._i18n = get_i18n(config_i18n=config_i18n)
        self._webhook_path = webhook_path
        self._secret_token = secret_token
        self._ip_address = ip_address
        self._allowed_updates = allowed_updates
        self.base_url: str | None = None
        self._payment_container: PaymentContainer | None = None

        # include middlewares
        self._setup_user_middleware()
        self._setup_session_middleware(session_factory=session_factory)
        self._setup_sender_middleware()
        if self._i18n is not None:
            self._setup_i18n_middleware()
        self._setup_windows_middleware()

    def include_middleware(
        self, middleware: BaseMiddleware, event: Literal["message", "callback_query"] | None = None
    ):
        if event is None:
            self.dispatcher.update.middleware(middleware)
            logger.info("Middleware is initialized to update events")
        elif event == "message":
            self.dispatcher.message.middleware(middleware)
            logger.info("Middleware is initialized to message events")
        elif event == "callback_query":
            self.dispatcher.callback_query.middleware(middleware)
            logger.info("Middleware is initialized to callback query events")
        else:
            raise ValueError("Invalid event type")

    def include_router(self, router: Router):
        self.dispatcher.include_router(router)
        logger.info("Router is initialized: %s", router)

    def include_routers(self, *routers: Router):
        self.dispatcher.include_routers(*routers)

    def include_services(
        self,
        event: Literal["message", "callback_query"] | None = None,
        **services: type[BaseService],
    ):
        self.include_middleware(middleware=ServiceMiddleware(**services), event=event)

    async def setup_webhook(self, public_url: str | None = None) -> str:
        if public_url is None:
            public_url = await get_ngrok_public_url()
        if public_url is None:
            raise RuntimeError("Public URL is not set")
        self.base_url = public_url
        if self.base_url is None:
            raise RuntimeError("Base URL is not set")
        url = f"{self.base_url}{self.webhook_path}"
        logger.info("Set webhook Telegram Bot: %s", url)
        await self.set_webhook(
            url=url,
            secret_token=self._secret_token,
            ip_address=self._ip_address,
            allowed_updates=self._allowed_updates
            if self._allowed_updates
            else self.dispatcher.resolve_used_update_types(),
            drop_pending_updates=True,
        )
        return self.base_url

    async def shutdown(self):
        logger.info("Shutdown bot")
        await self.delete_webhook(drop_pending_updates=False)
        if self.session is not None:
            await self.session.close()
        if self._redis is not None:
            await self._redis.shutdown()
        logger.info("Bot is shutdown")

    async def get_user_in_chat(
        self,
        chat_id: int,
        user_id: int,
        not_allowed_statuses: tuple[ChatMemberStatus, ...] = (
            ChatMemberStatus.KICKED,
            ChatMemberStatus.LEFT,
        ),
    ) -> bool:
        member = await self.get_chat_member(chat_id, user_id)
        return member.status not in not_allowed_statuses

    async def create_invite_link(
        self,
        chat_id: int,
        expire_date: datetime | timedelta | int | None = None,
        member_limit: int | None = None,
        creates_join_request: bool | None = None,
    ) -> str:
        chat = await super().create_chat_invite_link(
            chat_id=chat_id,
            expire_date=expire_date,
            member_limit=member_limit,
            creates_join_request=creates_join_request,
        )
        return chat.invite_link

    async def send_message_to_chat(
        self,
        window: type[BaseWindow],
        func: str,
        *,
        chat_id: int | None = None,
        user_id: int | None = None,
        locale: str | None = None,
        **kwargs,
    ):
        target_chat = chat_id or user_id
        if target_chat is None:
            raise ValueError("Either chat_id or user_id must be provided")

        if locale is None and user_id is not None:
            locale = await get_user_language(user_id, session_factory=self._session_factory)

        if not isinstance(target_chat, int):
            raise ValueError("Either user_id or chat_id must be provided")

        w = window(i18n=self.i18n, locale=locale or "ru")
        window_func = getattr(w, func, None)

        if window_func is None or not callable(window_func):
            raise AttributeError(f"Window method {func!r} is not found")
        message = window_func(**kwargs)
        try:
            if isinstance(message, WindowMessage) and target_chat is not None:
                if message.photo_filename is not None:
                    formatter = FileFormatting(redis=self.redis)
                    photo = await formatter.get_photo(message.photo_filename)
                    await self.send_photo(
                        chat_id=target_chat,
                        photo=photo,
                        caption=message.caption,
                        reply_markup=message.reply_markup,
                    )
                else:
                    await self.send_message(
                        chat_id=target_chat, text=message.text, reply_markup=message.reply_markup
                    )
        except Exception as e:
            logger.exception("Failed to send message: %s", e)

    def _setup_redis(self) -> RedisStorage | None:
        if self._redis is not None:
            storage = RedisStorage(
                redis=self.redis,
                state_ttl=self._redis.telegram_state_ttl,
                data_ttl=self._redis.telegram_data_ttl,
            )
            logger.info("Redis storage is initialized")
            return storage
        return None

    @property
    def dispatcher(self) -> Dispatcher:
        return self._dispatcher

    @property
    def i18n(self) -> I18n:
        if self._i18n is None:
            raise RuntimeError("I18n is not initialized")
        return self._i18n

    @property
    def cache(self) -> RedisCache:
        if self._redis is None:
            raise RuntimeError("Redis is not initialized")
        return self._redis

    @property
    def redis(self) -> Redis:
        return self.cache.redis

    @property
    def webhook_path(self) -> str:
        return self._webhook_path

    @property
    def payment_container(self) -> PaymentContainer:
        if self._payment_container is None:
            raise RuntimeError("Payment container is not initialized")
        return self._payment_container

    @payment_container.setter
    def payment_container(self, payment_container: PaymentContainer):
        self._payment_container = payment_container

    def _setup_sender_middleware(self):
        self.dispatcher.update.middleware(
            SenderMiddleware(formatter=FileFormatting(redis=self.redis))
        )

    def _setup_user_middleware(self):
        self.include_middleware(UserMiddleware())

    def _setup_session_middleware(self, session_factory: async_sessionmaker[AsyncSession]):
        self.include_middleware(SessionFactoryMiddleware(session_factory=session_factory))

    def _setup_i18n_middleware(self):
        if self._i18n is None:
            raise RuntimeError("I18n is not initialized")
        self.dispatcher.update.middleware(LanguageMiddleware(i18n=self.i18n))
        logger.info("I18n middleware is initialized")

    def _setup_windows_middleware(self):
        self.include_middleware(WindowsMiddleware(windows_container=WindowsContainer()))
