from dataclasses import dataclass

from aiogram import Dispatcher
from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker
from starlette.datastructures import State

from app.bot.core.base import TelegramBot
from app.bot.core.sender import BotSender
from app.infrastructure.payments.container import Payments


@dataclass(slots=True)
class ApplicationState:
    bot: TelegramBot
    dispatcher: Dispatcher
    base_url: str
    sender: BotSender

    session_factory: async_sessionmaker[AsyncSession] | None = None
    engine: AsyncEngine | None = None
    payments: Payments | None = None

    async def shutdown(self) -> None:
        if self.bot.session is not None:
            await self.bot.session.close()
        if self.engine is not None:
            await self.engine.dispose()
        if self.payments is not None:
            await self.payments.close()


def get_app_state(request: Request[State]) -> ApplicationState:
    state = getattr(request.app.state, "app_state", None)

    if not isinstance(state, ApplicationState):
        raise RuntimeError("AppState is not set in request.app.state")

    return state
