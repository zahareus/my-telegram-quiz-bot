from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import Chat
from uuid import UUID
import logging


class ChatRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.logger = logging.getLogger(__name__)

    async def get_by_uuid(self, chat_id: UUID) -> Chat | None:
        stmt = select(Chat).where(Chat.id == chat_id).limit(1)
        return await self.session.scalar(stmt)

    async def get_by_chat_id(self, chat_id: str) -> Chat | None:
        stmt = select(Chat).where(Chat.chat_id == chat_id).limit(1)
        return await self.session.scalar(stmt)

    async def create(self, chat_id: str, chat_title: str) -> Chat:
        chat = Chat(chat_id=chat_id, chat_title=chat_title)
        self.session.add(chat)
        await self.session.flush()
        self.logger.info(f"Chat {chat.id} created (chat_id: {chat.chat_id}), id: {chat.id}")
        return await self.get_by_uuid(chat.id)
