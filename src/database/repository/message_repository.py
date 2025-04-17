from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import Message
from uuid import UUID
import logging
from typing import List
import datetime


class MessageRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.logger = logging.getLogger(__name__)

    async def get_by_id(self, message_id: UUID) -> Message | None:
        stmt = select(Message).where(Message.id == message_id).limit(1)
        return await self.session.scalar(stmt)

    async def get_by_message_id(self, message_id: str) -> Message | None:
        stmt = select(Message).where(Message.message_id == message_id).limit(1)
        return await self.session.scalar(stmt)

    async def create(self, channel_uuid: UUID, message_id: str, message_text: str, timestamp: datetime.datetime) -> Message:
        message = Message(channel_id=channel_uuid,
                          message_id=message_id,
                          message_text=message_text,
                          timestamp=timestamp.replace(tzinfo=None))

        self.session.add(message)
        await self.session.flush()
        self.logger.info(
            f"Message {message.id} created (chat_id: {message.channel_id}, message_id: {message.message_id}), id: {message.id}")
        return await self.get_by_id(message.id)

    async def get_by_chat_uuid(self, channel_uuid: UUID, all_after: datetime.datetime = None) -> List[Message]:
        if all_after is not None:
            stmt = select(Message).where(Message.channel_id == channel_uuid, Message.timestamp > all_after)
        else:
            stmt = select(Message).where(Message.channel_id == channel_uuid)
        result = await self.session.scalars(stmt)
        messages = list(result.all())
        return messages
