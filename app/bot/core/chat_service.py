from enum import StrEnum

from aiogram import Bot
from aiogram.enums import ChatMemberStatus


class NotAllowedStatus(StrEnum):
    KICKED = ChatMemberStatus.KICKED
    LEFT = ChatMemberStatus.LEFT


class ChatService:
    def __init__(self, bot: Bot):
        self.bot: Bot = bot

    async def get_user_in_chat(self, chat_id: int, user_id: int) -> bool:
        member = await self.bot.get_chat_member(chat_id, user_id)
        return member.status not in NotAllowedStatus

    async def create_invite_link(self, chat_id: int) -> str:
        return (await self.bot.create_chat_invite_link(chat_id)).invite_link
