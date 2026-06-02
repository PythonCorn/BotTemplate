from typing import Any, TypeVar, Type

import orjson
from pydantic import BaseModel
from redis.asyncio import Redis

T = TypeVar("T", bound=BaseModel)


class RedisCache:
    def __init__(self, redis: Redis):
        self.redis = redis

    async def set(self, name: str, value: bytes | bytearray | str | int | float | list[T] | T, ttl: int | None = None):
        value = self._reformat_value_to_json(value)
        await self.redis.set(
            name=name,
            value=value,
            ex=ttl
        )

    async def get(self, name: str, response_model: Type[T] | list[Type[T]] | None = None) -> Any | list[T] | T | None:
        value = await self.redis.get(name)
        if value is None:
            return None
        if response_model:
            return self._reformat_value_to_pydantic(value, response_model)
        if isinstance(value, bytes):
            return value.decode("utf-8")
        return value

    @staticmethod
    def _reformat_value_to_pydantic(value: bytes | str, response_model: Type[T] | list[Type[T]]) -> T | list[T]:
        value = orjson.loads(value)
        if isinstance(response_model, list):
            return [response_model[0].model_validate(v) for v in value]
        return response_model.model_validate(value)

    @staticmethod
    def _reformat_value_to_json(
            value: bytes | bytearray | str | int | float | list[T] | T
    ) -> bytes | bytearray | str | int | float:

        if isinstance(value, BaseModel):
            return orjson.dumps(value.model_dump(mode="json"))

        if isinstance(value, list):
            return orjson.dumps([
                item.model_dump(mode="json") if isinstance(item, BaseModel) else item
                for item in value
            ])

        return value
