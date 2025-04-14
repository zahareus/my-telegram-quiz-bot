import logging
from src.database import ChatRepository, Chat
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.types import Message


class ChatService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.chat_repository = ChatRepository(session)
        self.logger = logging.getLogger(__name__)

    @staticmethod
    async def check_chat(message: Message) -> bool:
        return message.chat.type == 'channel'

    @staticmethod
    async def check_active(chat_field: Chat) -> bool:
        return chat_field.is_daily or chat_field.is_weekly

    async def get_by_chat_id(self, chat_id: str) -> Chat | None:
        chat_field = await self.chat_repository.get_by_chat_id(chat_id)
        return chat_field

    async def get_chat(self, message: Message) -> Chat | None:
        if not await self.check_chat(message):
            return None
        chat_field = await self.chat_repository.get_by_chat_id(str(message.chat.id))
        if chat_field is None:
            chat_name = None
            if message.chat.title:
                chat_name = message.chat.title
            chat_field = await self.chat_repository.create(
                chat_id=str(message.chat.id),
                chat_title=chat_name
            )
        return chat_field
