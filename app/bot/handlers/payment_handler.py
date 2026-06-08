from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message

from app.bot.core.base import TelegramBot
from app.bot.core.sender import Sender
from app.bot.windows.core.container import WindowsContainer
from app.bot.windows.payment_window import PaymentCallbackData, PaymentProvidersCallbackData
from app.database.models import User
from app.services.payment_service import PaymentService
from app.services.user_service import UserService

router = Router(name="payment_handler")


class PaymentStatesGroup(StatesGroup):
    amount = State()


@router.callback_query(PaymentCallbackData.filter())
async def show_payments(_, windows: WindowsContainer, sender: Sender, bot: TelegramBot):
    await sender.send(windows.payment.start(bot.payment_container))


@router.callback_query(PaymentProvidersCallbackData.filter())
async def get_payment_name(
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
    users: UserService,
    payments: PaymentService,
    bot: TelegramBot,
    sender: Sender,
    windows: WindowsContainer,
):
    data = await state.get_data()
    provider: str | None = data.get("provider")
    if provider is None:
        return
    payment_provider = bot.payment_container.get(provider)
    if payment_provider is None:
        return
    try:
        if msg.from_user is None:
            return
        user: User | None = await users.get_user_by_telegram_id(telegram_id=msg.from_user.id)
        if user is None:
            return
        if msg.text is None:
            return
        invoice_data = await payments.create_payment(
            user_id=user.user_id,
            provider=provider,
            amount=msg.text,
        )
        await payments.uow.commit()

        invoice = await payment_provider.create_invoice(
            invoice_id=invoice_data.id,
            amount=float(msg.text),
        )
        await sender.send(window=windows.payment.create_invoice(invoice))
    except ValueError:
        await sender.send(window=windows.payment.invalid_operation())
