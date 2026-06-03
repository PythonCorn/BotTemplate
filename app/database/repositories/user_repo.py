from sqlalchemy import select

from app.database.models import User
from app.database.repositories.base import BaseRepository


class UserRepo(BaseRepository[User]):
    async def get_by_user_id(self, user_id: int) -> User | None:
        user: User | None = await self.session.scalar(select(User).where(User.user_id == user_id))
        return user

    async def get_user_language(self, user_id: int) -> str:
        stmt = select(User.language).where(User.user_id == user_id)
        return await self.session.scalar(stmt) or "ru"
