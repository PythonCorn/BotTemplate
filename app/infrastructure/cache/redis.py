from datetime import timedelta
from typing import Any, TypeVar

import orjson
from pydantic import BaseModel
from redis.asyncio import Redis

T = TypeVar("T", bound=BaseModel)


class RedisCache:
    def __init__(
        self,
        redis: Redis,
        telegram_state_ttl: int | timedelta | None = None,
        telegram_data_ttl: int | timedelta | None = None,
    ):
        self.redis = redis
        self.telegram_state_ttl = telegram_state_ttl
        self.telegram_data_ttl = telegram_data_ttl

    async def set(
        self,
        name: str,
        value: bytes | bytearray | str | int | float | list[T] | T,
        ttl: int | None = None,
    ):
        value = self._reformat_value_to_json(value)
        await self.redis.set(name=name, value=value, ex=ttl)

    async def get(
        self, name: str, response_model: type[T] | list[type[T]] | None = None
    ) -> Any | list[T] | T | str | None:
        value = await self.redis.get(name)
        if value is None:
            return None
        if response_model:
            return self._reformat_value_to_pydantic(value, response_model)
        if isinstance(value, bytes):
            return value.decode("utf-8")
        return value

    async def delete(self, name: str):
        await self.redis.delete(name)

    @staticmethod
    def _reformat_value_to_pydantic(
        value: bytes | str, response_model: type[T] | list[type[T]]
    ) -> T | list[T]:
        value = orjson.loads(value)
        if isinstance(response_model, list):
            return [response_model[0].model_validate(v) for v in value]
        return response_model.model_validate(value)

    @staticmethod
    def _reformat_value_to_json(
        value: bytes | bytearray | str | int | float | list[T] | T,
    ) -> bytes | bytearray | str | int | float:

        if isinstance(value, BaseModel):
            return orjson.dumps(value.model_dump(mode="json"))

        if isinstance(value, list):
            return orjson.dumps(
                [
                    item.model_dump(mode="json") if isinstance(item, BaseModel) else item
                    for item in value
                ]
            )

        return value

    async def shutdown(self):
        await self.redis.close()
