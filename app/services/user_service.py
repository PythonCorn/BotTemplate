from app.database.models import User
from app.services.base import BaseService


class UserService(BaseService):
    async def add_new_user(self, user_id: int, username: str | None = None) -> User:
        user = await self.uow.users.get_by_user_id(user_id)
        if user is None:
            user = await self.uow.users.add(User(user_id=user_id, username=username))
        return user

    async def get_user_language(self, user_id: int) -> str:
        return await self.uow.users.get_user_language(user_id)
