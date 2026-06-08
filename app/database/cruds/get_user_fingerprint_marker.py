import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.database.models import User

logger = logging.getLogger(__name__)


async def get_user_fingerprint_marker(
    user_id: int, session_factory: async_sessionmaker[AsyncSession]
) -> bool:
    async with session_factory() as session:
        stmt = select(User.is_check_fingerprint).where(User.user_id == user_id)
        result = await session.scalar(stmt)
        if not result:
            return False
        logger.info("User is pushed fingerprint %s", result)
        return result
