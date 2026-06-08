import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.database.models import User

logger = logging.getLogger(__name__)


async def get_user_language(user_id: int, session_factory: async_sessionmaker[AsyncSession]) -> str:
    async with session_factory() as session:
        stmt = select(User.language).where(User.user_id == user_id)
        result = await session.scalar(stmt)
        if not result:
            return "ru"
        logger.info("User language %s", result)
        return result
