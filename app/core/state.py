from dataclasses import dataclass

from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker
from starlette.datastructures import State

from app.bot.core.base import TelegramBot
from app.infrastructure.payments.providers.core.container import PaymentContainer


@dataclass(slots=True)
class AppState:
    # Telegram states
    bot: TelegramBot

    # Database states
    session_factory: async_sessionmaker[AsyncSession]
    engine: AsyncEngine

    # Payment states
    payments: PaymentContainer | None = None

    # Base url
    base_url: str = ""

    async def shutdown(self) -> None:
        await self.bot.shutdown()
        await self.engine.dispose()
        if self.payments is not None:
            await self.payments.close()


def get_app_state(request: Request[State]) -> AppState:
    state = getattr(request.app.state, "app_state", None)

    if not isinstance(state, AppState):
        raise RuntimeError("AppState is not set in request.app.state")

    return state
