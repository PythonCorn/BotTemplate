from functools import cached_property

from app.database.unit_of_work import UnitOfWork
from app.infrastructure.cache.redis import RedisCache
from app.services.user_service import UserService


class ServiceContainer:
    def __init__(self, uow: UnitOfWork, redis: RedisCache | None = None):
        self.uow = uow
        self.redis = redis

    @cached_property
    def users(self) -> UserService:
        return UserService(self.uow)
