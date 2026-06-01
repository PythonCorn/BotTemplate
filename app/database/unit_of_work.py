from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession


class UnitOfWork:
    def __init__(self, async_session_factory: async_sessionmaker[AsyncSession]):
        self.async_session_factory = async_session_factory
        self.session: AsyncSession = None # type: ignore

    async def commit(self) -> None:
        await self.session.commit()

    async def rollback(self) -> None:
        await self.session.rollback()

    async def __aenter__(self) -> "UnitOfWork":
        self.session = self.async_session_factory()
        # Repositories are injected here

        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        if exc_type:
            await self.rollback()
        await self.session.close()