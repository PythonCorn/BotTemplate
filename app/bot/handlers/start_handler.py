import logging

from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message, User

from app.bot.core.get_user_data import get_user_data
from app.services.container import ServiceContainer

router = Router(name="start_handler")

logger = logging.getLogger(__name__)


@router.message(CommandStart())
async def pushed_start(msg: Message, services: ServiceContainer):
    user_service = services.users
    telegram_user: User = get_user_data(msg)
    user = await user_service.add_new_user(
        user_id=telegram_user.id, username=telegram_user.username
    )
    member = await services.bot.get_user_in_chat(chat_id=-1003731639160, user_id=user.user_id)
    logger.info(f"User {user.user_id} is in chat: {member}")
    photo = await services.photo_formatter.get_photo("example.png")
    message = await msg.answer_photo(
        **services.windows.example.start(username=user.username), photo=photo
    )
    await services.photo_formatter.save_photo_in_cache(message, "example.png")
