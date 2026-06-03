# app/core/bootstrap.py
from aiogram import Bot, Dispatcher, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.utils.i18n import I18n
from redis.asyncio import Redis

from app.bot.core.chat_service import ChatService
from app.bot.middlewares.language_middleware import LanguageMiddleware
from app.bot.middlewares.service_middleware import ServiceMiddleware
from app.bot.windows.container import WindowsContainer
from app.core.config import settings
from app.core.container import Container
from app.database.session import async_session_factory
from app.infrastructure.cache.redis import RedisCache
from app.infrastructure.payments.container import PaymentContainer
from app.infrastructure.payments.cryptobot_provider import CryptobotProvider


def _create_redis():
    return Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        db=settings.REDIS_DB,
        password=settings.REDIS_PASSWORD or None,
    )


def _create_payment_container() -> PaymentContainer:
    # Add your payment provider here
    cryptobot = (
        CryptobotProvider(token=settings.CRYPTOBOT_TOKEN) if settings.CRYPTOBOT_TOKEN else None
    )

    return PaymentContainer(
        cryptobot=cryptobot,
    )


def _create_bot() -> Bot:
    return Bot(
        token=settings.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )


def _create_dispatcher(redis: Redis) -> Dispatcher:
    storage = RedisStorage(redis=redis, state_ttl=60 * 60 * 2)
    return Dispatcher(storage=storage)


def _setup_i18n(dispatcher: Dispatcher):
    i18n = I18n(path="app/locales", default_locale="ru")
    dispatcher.update.middleware(LanguageMiddleware(i18n=i18n))


def _get_windows_container() -> WindowsContainer:
    return WindowsContainer()


def _setup_service_middleware(
    dispatcher: Dispatcher,
    redis: Redis,
    payment_container: PaymentContainer,
    chat_service: ChatService,
):
    dispatcher.update.middleware(
        ServiceMiddleware(
            async_session_factory=async_session_factory,
            redis=RedisCache(redis=redis),
            payment_container=payment_container,
            chat_service=chat_service,
            windows_container=_get_windows_container(),
        )
    )


def _create_chat_service(bot: Bot) -> ChatService:
    return ChatService(bot=bot)


def setup_bot_routers(routers: list[Router], dispatcher: Dispatcher):
    dispatcher.include_routers(*routers)


def create_container(routers: list[Router]) -> Container:
    redis = _create_redis()
    payment_container = _create_payment_container()

    bot = _create_bot()
    dp = _create_dispatcher(redis=redis)

    _setup_service_middleware(
        dispatcher=dp,
        redis=redis,
        payment_container=payment_container,
        chat_service=_create_chat_service(bot=bot),
    )

    _setup_i18n(dp)

    setup_bot_routers(routers=routers, dispatcher=dp)

    return Container(
        bot=bot,
        dp=dp,
        redis=redis,
        session_factory=async_session_factory,
        payments=payment_container,
    )
