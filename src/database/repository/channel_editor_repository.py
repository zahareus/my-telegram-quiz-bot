from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import ChannelEditor, Channel, User
from uuid import UUID
import logging

from typing import List


class ChannelEditorRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.logger = logging.getLogger(__name__)

    async def get_by_uuid(self, channel_editor_id: UUID) -> ChannelEditor | None:
        stmt = select(ChannelEditor).where(ChannelEditor.id == channel_editor_id).limit(1)
        return await self.session.scalar(stmt)

    async def get_by_channel_uuid(self, channel_uuid: UUID) -> List[User]:
        stmt = (
            select(User)
            .join(ChannelEditor, ChannelEditor.user_id == User.id)
            .where(ChannelEditor.channel_id == channel_uuid)
        )
        result = await self.session.scalars(stmt)
        channel_editors = list(result.all())
        return channel_editors

    async def create(self, channel_uuid: UUID, user_uuid: UUID) -> ChannelEditor:
        chat_editor = ChannelEditor(channel_id=channel_uuid, user_id=user_uuid)
        self.session.add(chat_editor)
        await self.session.flush()
        self.logger.info(f"ChannelEditor {chat_editor.id} created (chat_id: {chat_editor.channel_id},"
                         f"user_id: {chat_editor.user_id}), id: {chat_editor.id}")
        return await self.get_by_uuid(chat_editor.id)

    async def get_by_channel_and_user(
        self, channel_id: UUID, user_id: UUID
    ) -> ChannelEditor | None:
        stmt = (
            select(ChannelEditor)
            .where(ChannelEditor.channel_id == channel_id, ChannelEditor.user_id == user_id)
            .limit(1)
        )
        return await self.session.scalar(stmt)
