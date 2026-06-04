import logging

from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message, User

from app.bot.core.chat_service import ChatService
from app.bot.core.get_user_data import get_user_data
from app.bot.windows.core.container import WindowsContainer
from app.bot.windows.core.sender import Sender
from app.bot.windows.payment_window import PaymentCallbackData, PaymentProvidersCallbackData
from app.database.models import User as DatabaseUser
from app.infrastructure.payments import PaymentContainer
from app.services.container import ServiceContainer

router = Router(name="start_handler")

logger = logging.getLogger(__name__)


class PaymentStatesGroup(StatesGroup):
    amount = State()


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
    window = windows.payment.start(payment_container=payments)
    await sender.send(window)


@router.callback_query(PaymentProvidersCallbackData.filter())
async def get_amount(
    _,
    windows: WindowsContainer,
    sender: Sender,
    callback_data: PaymentProvidersCallbackData,
    state: FSMContext,
):
    await state.clear()
    provider = callback_data.provider
    await state.update_data(provider=provider)
    await state.set_state(PaymentStatesGroup.amount)
    await sender.send(window=windows.payment.send_amount())


@router.message(PaymentStatesGroup.amount)
async def get_amount_message(
    msg: Message,
    state: FSMContext,
    payments: PaymentContainer,
    services: ServiceContainer,
    sender: Sender,
    windows: WindowsContainer,
):
    data = await state.get_data()
    provider = data["provider"]
    payment_provider = payments.get(provider)
    if payment_provider is None:
        return
    try:
        if msg.from_user is None:
            return
        user: DatabaseUser | None = await services.users.get_user_by_telegram_id(
            telegram_id=msg.from_user.id
        )
        if user is None:
            return
        if msg.text is None:
            return
        invoice_data = await services.payments.add_new_payment(
            user_id=user.id,
            provider=provider,
            amount=msg.text,
        )

        invoice = await payment_provider.create_invoice(
            invoice_id=invoice_data.id,
            amount=float(msg.text),
        )
        await sender.send(window=windows.payment.create_invoice(invoice))
    except ValueError:
        await sender.send(window=windows.payment.invalid_operation())
