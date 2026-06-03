import logging

from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message, User

from app.services.container import ServiceContainer

router = Router(name="start_handler")

logger = logging.getLogger(__name__)


@router.message(CommandStart())
async def pushed_start(msg: Message, services: ServiceContainer):
    user_service = services.users
    tg_user: User | None = msg.from_user
    if tg_user is None:
        return
    user = await user_service.add_new_user(user_id=tg_user.id, username=tg_user.username)
    print(user)
    await msg.answer("Hello, world!")
