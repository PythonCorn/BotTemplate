from functools import cached_property

from app.database.unit_of_work import UnitOfWork
from app.infrastructure.cache.redis import RedisCache
from app.infrastructure.payments.container import PaymentContainer
from app.services.user_service import UserService


class ServiceContainer:
    def __init__(self, uow: UnitOfWork, redis: RedisCache, payment_container: PaymentContainer):
        self.uow = uow
        self.redis = redis
        self.payment_container = payment_container

    @cached_property
    def users(self) -> UserService:
        return UserService(self.uow)

    @property
    def payments(self) -> PaymentContainer:
        return self.payment_container

    @property
    def cache(self) -> RedisCache:
        return self.redis
