import logging
from src.database import ChannelRepository, Channel
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.types import Message

from typing import List


class ChannelService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.channel_repository = ChannelRepository(session)
        self.logger = logging.getLogger(__name__)

    @staticmethod
    async def check_channel(message: Message) -> bool:
        return message.chat.type == 'channel'

    @staticmethod
    async def check_active(channel_field: Channel) -> bool:
        return channel_field.is_daily or channel_field.is_weekly

    async def get_by_channel_id(self, channel_id: str) -> Channel | None:
        chat_field = await self.channel_repository.get_by_channel_id(channel_id)
        return chat_field

    async def get_or_create_message(self, message: Message) -> Channel | None:
        if not await self.check_channel(message):
            return None
        channel_field = await self.channel_repository.get_by_channel_id(str(message.chat.id))
        if channel_field is None:
            channel_title = None
            if message.chat.title:
                channel_title = message.chat.title
            channel_field = await self.channel_repository.create(
                channel_id=str(message.chat.id),
                channel_title=channel_title
            )
        return channel_field

    async def get_or_create_id(self, channel_id: str, title: str) -> Channel | None:
        channel_field = await self.channel_repository.get_by_channel_id(channel_id)
        if channel_field is None:
            channel_field = await self.channel_repository.create(
                channel_id=channel_id,
                channel_title=title
            )
        return channel_field

    @staticmethod
    async def set_active(channel_field: Channel, is_active: bool = True) -> None:
        channel_field.is_active = is_active

    async def get_active(self) -> List[Channel]:
        channels = await self.channel_repository.get_active()
        return channels

    async def get_daily(self) -> List[Channel]:
        channels = await self.channel_repository.get_daily()
        return channels

    async def get_weekly(self) -> List[Channel]:
        channels = await self.channel_repository.get_weekly()
        return channels
