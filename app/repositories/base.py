from typing import TypeVar, Generic, Sequence

from sqlalchemy import select, exists, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.base import BaseModel

T = TypeVar("T", bound=BaseModel)


class BaseRepository(Generic[T]):
    def __init__(
            self,
            session: AsyncSession,
            model: type[T],
    ):
        self.session = session
        self.model = model

    async def add(self, instance: T) -> T:
        self.session.add(instance)
        await self.session.flush()
        return instance

    async def get_by_id(self, model_id: int) -> T | None:
        return await self.session.get(self.model, model_id)

    async def get_all(
            self,
            *,
            limit: int | None = None,
            offset: int | None = None,
    ) -> Sequence[T]:
        stmt = select(self.model)

        if limit is not None:
            stmt = stmt.limit(limit)

        if offset is not None:
            stmt = stmt.offset(offset)

        result = await self.session.scalars(stmt)
        return result.all()

    async def exists_by_id(self, model_id: int) -> bool:
        stmt = select(
            exists().where(self.model.id == model_id)
        )

        return bool(await self.session.scalar(stmt))

    async def count(self) -> int:
        stmt = select(func.count()).select_from(self.model)

        return await self.session.scalar(stmt) or 0

    async def delete(self, instance: T) -> None:
        await self.session.delete(instance)
        await self.session.flush()

    async def delete_by_id(self, model_id: int) -> bool:
        instance = await self.get_by_id(model_id)

        if instance is None:
            return False

        await self.delete(instance)
        return True


