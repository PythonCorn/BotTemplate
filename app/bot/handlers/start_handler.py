import logging

from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.fsm.state import State, StatesGroup

from app.bot.core.sender import Sender
from app.bot.middlewares.user_middleware import TelegramUser
from app.bot.windows.core.container import WindowsContainer
from app.bot.windows.core.keyboards import StartCallbackData
from app.services.user_service import UserService

router = Router(name="start_handler")

logger = logging.getLogger(__name__)


class PaymentStatesGroup(StatesGroup):
    amount = State()


@router.message(CommandStart())
@router.callback_query(StartCallbackData.filter())
async def check(
    _, windows: WindowsContainer, sender: Sender, users: UserService, telegram_user: TelegramUser
):
    user = await users.add_new_user(user_id=telegram_user.id, username=telegram_user.username)
    await sender.send(windows.start.start(username=user.username))
