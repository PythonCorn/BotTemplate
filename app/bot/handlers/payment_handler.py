import contextlib

from aiogram import Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message

from app.bot.core.base import TelegramBot
from app.bot.core.sender import Sender
from app.bot.windows.core.container import Windows
from app.bot.windows.payment_window import PaymentCallbackData, PaymentProvidersCallbackData
from app.database.models import User
from app.infrastructure.payments.providers.core.exceptions import PaymentException
from app.services.container import Services

router = Router(name="payment_handler")


class PaymentStatesGroup(StatesGroup):
    amount = State()


@router.callback_query(PaymentCallbackData.filter())
async def show_payments(_, windows: Windows, sender: Sender, bot: TelegramBot):
    await sender.send(windows.payment.start(bot.payments))


@router.callback_query(PaymentProvidersCallbackData.filter())
async def get_payment_name(
    call: CallbackQuery,
    windows: Windows,
    sender: Sender,
    callback_data: PaymentProvidersCallbackData,
    state: FSMContext,
):
    await state.clear()
    provider = callback_data.provider
    await state.update_data(provider=provider)
    await state.set_state(PaymentStatesGroup.amount)
    await sender.send(window=windows.payment.send_amount())
    if isinstance(call.message, Message):
        await sender.add_message_to_cache(
            chat_id=call.from_user.id,
            message_id=call.message.message_id,
            key="payment_window",
        )


@router.message(PaymentStatesGroup.amount)
async def get_amount_message(
    msg: Message,
    state: FSMContext,
    services: Services,
    bot: TelegramBot,
    sender: Sender,
    windows: Windows,
):
    data = await state.get_data()
    provider_name = data.get("provider")
    if provider_name is None:
        raise ValueError("Provider is not set")
    try:
        if bot.payments is None:
            raise PaymentException("Payments are not enabled")
        provider = bot.payments.get(provider_name)
        if msg.from_user is None:
            raise PaymentException("User is not found")
        user: User | None = await services.users.get_user_by_telegram_id(
            telegram_id=msg.from_user.id
        )
        if user is None:
            raise PaymentException("User is not found")
        if msg.text is None:
            raise ValueError("Amount is not set")
        invoice_data = await services.payments.create_payment(
            user_id=user.user_id,
            provider_name=provider_name,
            amount=msg.text,
        )
        if provider is None:
            raise PaymentException("Provider is not found")
        invoice = await provider.create_invoice(
            invoice_id=invoice_data.id,
            amount=float(msg.text),
        )
        await state.clear()
        await sender.edit_message_in_chat(
            chat_id=msg.from_user.id,
            key="payment_window",
            message=windows.payment.create_invoice(invoice),
        )
    except ValueError:
        await sender.send(window=windows.payment.invalid_operation())
    except PaymentException:
        await sender.send(window=windows.exceptions.exception_message())
    finally:
        with contextlib.suppress(TelegramBadRequest):
            await msg.delete()
