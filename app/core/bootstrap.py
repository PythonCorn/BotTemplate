# app/core/bootstrap.py
from aiogram import Dispatcher, Router

from app.bot.core import create_bot, create_dispatcher, setup_i18n
from app.bot.core.chat_service import ChatService
from app.bot.handlers.setup_handlers import setup_handlers
from app.bot.middlewares import setup_service_middleware
from app.core.config import settings
from app.core.container import Container
from app.database.session import async_session_factory
from app.infrastructure.cache import setup_redis
from app.infrastructure.payments import create_payment_container
from app.infrastructure.payments.cryptobot_provider import CryptobotProvider


def setup_bot_routers(routers: list[Router], dispatcher: Dispatcher):
    dispatcher.include_routers(*routers)


def create_container() -> Container:
    redis = setup_redis()  # Создание глобального кэша

    payment_container = create_payment_container(
        cryptobot_provider=CryptobotProvider(
            token=settings.CRYPTOBOT_TOKEN
        )  # Подключение платежных сервисов
    )  # Контейнер для платежей

    bot = create_bot()
    dp = create_dispatcher(redis=redis)

    setup_service_middleware(
        dispatcher=dp,
        redis=redis,
        payment_container=payment_container,
        chat_service=ChatService(bot=bot),
    )

    i18n = setup_i18n(dp)  # Подключение Babel

    setup_handlers(dispatcher=dp)

    return Container(
        bot=bot,
        dp=dp,
        redis=redis,
        session_factory=async_session_factory,
        payments=payment_container,
        i18n=i18n,
    )
