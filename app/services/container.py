from functools import cached_property

from app.bot.core.chat_service import ChatService
from app.bot.core.file_formatting import FileFormatting
from app.bot.windows.container import WindowsContainer
from app.database.unit_of_work import UnitOfWork
from app.infrastructure.cache.redis import RedisCache
from app.infrastructure.payments.container import PaymentContainer
from app.services.payment_service import PaymentService
from app.services.user_service import UserService


class ServiceContainer:
    def __init__(
        self,
        uow: UnitOfWork,
        redis: RedisCache,
        payment_container: PaymentContainer,
        chat_service: ChatService,
        windows_container: WindowsContainer,
    ):
        self.uow = uow
        self.redis = redis
        self._payment_container = payment_container
        self._chat_service = chat_service
        self._windows_container = windows_container
        self.photo_formatter = FileFormatting(redis=redis.redis)

    @cached_property
    def users(self) -> UserService:
        return UserService(self.uow)

    @cached_property
    def payment_service(self) -> PaymentService:
        return PaymentService(self.uow)

    @property
    def payments(self) -> PaymentContainer:
        return self._payment_container

    @property
    def cache(self) -> RedisCache:
        return self.redis

    @property
    def bot(self) -> ChatService:
        return self._chat_service

    @property
    def windows(self) -> WindowsContainer:
        return self._windows_container
