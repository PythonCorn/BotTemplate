import logging

from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message

from app.bot.core.base import TelegramBot
from app.bot.core.sender import Sender
from app.bot.windows.core.container import Windows
from app.bot.windows.core.keyboards import StartCallbackData
from app.services.container import Services

router = Router(name="start_handler")

logger = logging.getLogger(__name__)


class PaymentStatesGroup(StatesGroup):
    amount = State()


@router.message(CommandStart())
@router.callback_query(StartCallbackData.filter())
async def check(
    msg: Message, windows: Windows, sender: Sender, services: Services, bot: TelegramBot
):
    user = await services.users.add_new_user(
        user_id=msg.from_user.id,  # type: ignore
        username=msg.from_user.username,  # type: ignore
    )
    await sender.send(
        windows.start.start(
            username=user.username, public_url=bot.public_url, web_app_path=bot.web_app_webhook_path
        )
    )
