import logging
from datetime import datetime, timedelta
from inspect import signature
from typing import Any, Literal

from aiogram import BaseMiddleware, Bot, Dispatcher, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ChatMemberStatus, ParseMode
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.types import InputMediaPhoto
from aiogram.utils.i18n import I18n
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.bot.core.file_formatting import FileFormatting
from app.bot.middlewares.fingerprint_middleware import FingerprintMiddleware
from app.bot.middlewares.sender_middleware import SenderMiddleware
from app.bot.middlewares.service_middleware import ServiceMiddleware
from app.bot.middlewares.session_factory_middleware import SessionFactoryMiddleware
from app.bot.middlewares.user_middleware import UserMiddleware
from app.bot.middlewares.windows_middleware import WindowsMiddleware
from app.bot.windows.core.container import WindowsContainer
from app.bot.windows.core.window_message import WindowMessage
from app.infrastructure.cache.redis import RedisCache
from app.infrastructure.payments.providers.core.base import PaymentProvider
from app.infrastructure.payments.providers.core.container import PaymentContainer
from app.infrastructure.payments.providers.core.enums import PaymentProviderName
from app.infrastructure.payments.providers.core.exceptions import (
    PaymentContainerIsNotSet,
    PaymentProviderIsNotFound,
    PaymentProviderNameIsEmpty,
)
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
        i18n: I18n | None = None,
        redis: RedisCache | None = None,
        webhook_path: str = "/webhook/bot",
        fingerprint: bool = False,
    ):
        super().__init__(token=token, default=DefaultBotProperties(parse_mode=parse_mode))

        self.base_url: str | None = None
        self._session_factory = session_factory
        self._redis = redis
        self._dispatcher = Dispatcher(storage=self._setup_redis())
        self._i18n = i18n
        self._webhook_path = webhook_path
        self._secret_token = secret_token
        self._ip_address = ip_address
        self._allowed_updates = allowed_updates
        self._payment_container: PaymentContainer | None = None

        # include middlewares

        self._setup_user_middleware()
        self._setup_windows_middleware()
        self._setup_session_middleware(session_factory=session_factory)
        self._setup_sender_middleware()

        if fingerprint:
            self._setup_fingerprint_middleware()

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

    @staticmethod
    def _call_with_supported_kwargs(func, **kwargs):
        params = signature(func).parameters
        filtered_kwargs = {key: value for key, value in kwargs.items() if key in params}
        return func(**filtered_kwargs)

    async def send_message_to_chat(self, chat_id: int, message: WindowMessage):

        if message.photo_filename is not None:
            formatter = FileFormatting(redis=self.redis)
            photo = await formatter.get_photo(message.photo_filename)
            send = self.send_photo(
                chat_id=chat_id,
                photo=photo,
                caption=message.caption,
                reply_markup=message.reply_markup,
            )
        else:
            send = self.send_message(
                chat_id=chat_id, text=message.text, reply_markup=message.reply_markup
            )
        try:
            await send
        except Exception as e:
            logger.exception("Failed to send message: %s", e)

    async def edit_message_in_chat(self, chat_id: int, key: str, message: WindowMessage):
        message_id: Any = await self.cache.get(f"{key}:{chat_id}")
        message_id = int(message_id)
        if message_id is None:
            await self.send_message_to_chat(chat_id, message)
            await self.delete_message_in_chat(chat_id, key)
            return None
        try:
            if message.photo_filename is not None:
                return await self._edit_message_media(chat_id, message_id, message)

            return await self._edit_message_caption(chat_id, message_id, message)
        except Exception as e:
            logger.exception("Failed to send message: %s", e)
            try:
                return await self._edit_message_text(chat_id, message_id, message)
            except Exception as e:
                logger.exception("Failed to send message: %s", e)

    async def _edit_message_media(self, chat_id: int, message_id: int, message: WindowMessage):
        formatter = FileFormatting(redis=self.redis)
        photo = await formatter.get_photo(message.photo_filename)  # type: ignore
        return await self.edit_message_media(
            chat_id=chat_id,
            message_id=message_id,
            media=InputMediaPhoto(
                media=photo,
                caption=message.caption,
            ),
            reply_markup=message.reply_markup,  # type: ignore
        )

    async def _edit_message_caption(self, chat_id: int, message_id: int, message: WindowMessage):
        caption = message.caption if message.caption != "" else message.text
        return await self.edit_message_caption(
            chat_id=chat_id,
            message_id=message_id,
            caption=caption,
            reply_markup=message.reply_markup,  # type: ignore
        )

    async def _edit_message_text(self, chat_id: int, message_id: int, message: WindowMessage):
        text = message.text if message.text != "" else message.caption
        return await self.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=text,
            reply_markup=message.reply_markup,  # type: ignore
        )

    async def add_message_to_cache(
        self, chat_id: int, message_id: int, key: str, ttl: int = 60 * 5
    ):
        await self.cache.set(f"{key}:{chat_id}", message_id, ttl=ttl)
        logger.info("Message_id add to cache - %d", message_id)

    async def delete_message_in_chat(self, chat_id: int, key: str):
        message_id: Any = await self.cache.get(f"{key}:{chat_id}")
        if message_id is not None and isinstance(message_id, str) and message_id.isdigit():
            try:
                await self.delete_message(chat_id=chat_id, message_id=int(message_id))
                logger.info("Message %d deleted from chat %d", int(message_id), chat_id)
                await self.cache.delete(f"{key}:{chat_id}")
            except TelegramBadRequest:
                logger.exception(
                    "Can't delete message in chat %d, message_id %d", chat_id, message_id
                )

    def get_payment_provider(
        self, provider_name: str | PaymentProviderName | None
    ) -> tuple[PaymentProvider, str | PaymentProviderName]:
        """
        Fetches and returns the payment provider by its name.

        This method retrieves a payment provider from the designated payment container
        using the specified provider name. If the provider name is not supplied, the
        payment container is not set, or the provider cannot be found, corresponding
        exceptions are raised.

        Args:
            provider_name: The name of the payment provider to be fetched. It can be
                provided as a string, an instance of `PaymentProviderName`, or `None`.

        Raises:
            PaymentProviderNameIsEmpty: If the `provider_name` argument is `None`.
            PaymentContainerIsNotSet: If the payment container is not set.
            PaymentProviderIsNotFound: If no provider with the given name exists in the
                payment container.

        Returns:
            PaymentProvider: The payment provider object matching the supplied name.
        """
        if provider_name is None:
            raise PaymentProviderNameIsEmpty("Payment provider name is empty.")
        container = self.payment_container
        if container is None:
            raise PaymentContainerIsNotSet("Payment container is not set.")
        provider = container.get(provider_name)
        if provider is None:
            raise PaymentProviderIsNotFound("Provider %s is not found", provider_name)
        return provider, provider_name

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
    def payment_container(self) -> PaymentContainer | None:
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

    def _setup_windows_middleware(self):
        if self._i18n is None:
            raise RuntimeError("I18n is not initialized")
        self.include_middleware(
            WindowsMiddleware(windows_container=WindowsContainer(i18n=self.i18n))
        )

    def _setup_fingerprint_middleware(self):
        self.include_middleware(middleware=FingerprintMiddleware())
