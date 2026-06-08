from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from app.database.models import Fingerprint, Payment, User
from app.database.repositories.fingerprint import FingerprintRepository
from app.database.repositories.payment_repo import PaymentRepository
from app.database.repositories.user_repo import UserRepo


class UnitOfWork:
    def __init__(self, async_session_factory: async_sessionmaker[AsyncSession]):
        self.async_session_factory = async_session_factory
        self.session: AsyncSession | None = None
        self._committed = False

    async def flush(self) -> None:
        if self.session is None:
            raise RuntimeError("Session is not initialized")
        await self.session.flush()

    async def refresh(self, *instances: DeclarativeBase) -> None:
        if self.session is None:
            raise RuntimeError("Session is not initialized")
        for instance in instances:
            await self.session.refresh(instance)

    async def commit(self) -> None:
        if self.session is None:
            raise RuntimeError("Session is not initialized")
        await self.session.commit()
        self._committed = True

    async def rollback(self) -> None:
        if self.session is None:
            raise RuntimeError("Session is not initialized")
        await self.session.rollback()

    async def __aenter__(self) -> "UnitOfWork":
        self.session = self.async_session_factory()

        if self.session is None:
            raise RuntimeError("Session is not initialized")

        # Repositories are injected here
        self.users = UserRepo(self.session, User)
        self.payments = PaymentRepository(self.session, Payment)
        self.fingerprints = FingerprintRepository(self.session, Fingerprint)

        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        if self.session is None:
            raise RuntimeError("Session is not initialized")

        try:
            if exc_type or not self._committed:
                await self.rollback()
        finally:
            await self.session.close()
