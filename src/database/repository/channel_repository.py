from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import Channel
from uuid import UUID
import logging

from typing import List


class ChannelRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.logger = logging.getLogger(__name__)

    async def get_by_uuid(self, channel_uuid: UUID) -> Channel | None:
        stmt = select(Channel).where(Channel.id == channel_uuid).limit(1)
        return await self.session.scalar(stmt)

    async def get_by_channel_id(self, channel_id: str) -> Channel | None:
        stmt = select(Channel).where(Channel.channel_id == channel_id).limit(1)
        return await self.session.scalar(stmt)

    async def create(self, channel_id: str, channel_title: str) -> Channel:
        channel = Channel(channel_id=channel_id, channel_title=channel_title)
        self.session.add(channel)
        await self.session.flush()
        self.logger.info(f"Channel {channel.id} created (channel_id: {channel.channel_id}), id: {channel.id}")
        return await self.get_by_uuid(channel.id)

    async def get_active(self) -> List[Channel]:
        stmt = select(Channel).where(Channel.is_active == True)
        result = await self.session.scalars(stmt)
        channels = list(result.all())
        return channels

    async def get_daily(self) -> List[Channel]:
        stmt = select(Channel).where(Channel.is_daily == True)
        result = await self.session.scalars(stmt)
        channels = list(result.all())
        return channels