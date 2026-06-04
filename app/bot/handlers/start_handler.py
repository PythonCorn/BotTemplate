import logging

from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.types import CallbackQuery, Message, User

from app.bot.core.chat_service import ChatService
from app.bot.core.get_user_data import get_user_data
from app.bot.windows.core.container import WindowsContainer
from app.bot.windows.core.sender import Sender
from app.bot.windows.payment_window import PaymentCallbackData
from app.infrastructure.payments import PaymentContainer
from app.services.container import ServiceContainer

router = Router(name="start_handler")

logger = logging.getLogger(__name__)


@router.message(CommandStart())
@router.callback_query(F.data == "start")
async def pushed_start(
    event: Message | CallbackQuery,
    services: ServiceContainer,
    chat_service: ChatService,
    windows: WindowsContainer,
    sender: Sender,
):
    telegram_user: User = get_user_data(event)
    user = await services.users.add_new_user(
        user_id=telegram_user.id, username=telegram_user.username
    )
    member = await chat_service.get_user_in_chat(chat_id=-1003731639160, user_id=user.user_id)
    logger.info(f"User {user.user_id} is in chat: {member}")
    window = windows.example.start(username=user.username)
    await sender.send(window)


@router.callback_query(PaymentCallbackData.filter())
async def show_payments(_, windows: WindowsContainer, payments: PaymentContainer, sender: Sender):
    alert = windows.payment.attention()
    window = windows.payment.start(payment_container=payments)
    await sender.send(window, alert=alert)
