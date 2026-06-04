import logging

from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.types import CallbackQuery, Message, User

from app.bot.core.get_user_data import get_user_data
from app.services.container import ServiceContainer

router = Router(name="start_handler")

logger = logging.getLogger(__name__)


@router.message(CommandStart())
@router.callback_query(F.data == "start")
async def pushed_start(event: Message | CallbackQuery, services: ServiceContainer):
    user_service = services.users
    telegram_user: User = get_user_data(event)
    user = await user_service.add_new_user(
        user_id=telegram_user.id, username=telegram_user.username
    )
    member = await services.bot.get_user_in_chat(chat_id=-1003731639160, user_id=user.user_id)
    logger.info(f"User {user.user_id} is in chat: {member}")
    photo = await services.photo_formatter.get_photo("example.png")
    mes = services.windows.example.start(username=user.username).as_dict()
    if isinstance(event, Message):
        message = await event.answer_photo(**mes, photo=photo)
        await services.photo_formatter.save_photo_in_cache(message, "example.png")
    else:
        if isinstance(event.message, Message):
            await event.message.edit_caption(**mes)


@router.callback_query(F.data == "payment")
async def show_payments(call: CallbackQuery, services: ServiceContainer):
    if isinstance(call.message, Message):
        await call.message.edit_caption(
            **services.windows.payment.start(payment_container=services.payments).as_dict()
        )
