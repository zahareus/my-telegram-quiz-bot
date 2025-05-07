import logging
from src.database import ChannelEditorRepository, Channel, User
from .channel_service import ChannelService
from .user_service import UserService
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.types import Message
from uuid import UUID

from typing import List


class ChannelEditorService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.channel_editor_repository = ChannelEditorRepository(session)
        self.chat_service = ChannelService(session)
        self.user_service = UserService(session)
        self.logger = logging.getLogger(__name__)

    async def get_by_channel(self, channel_instance: str | Channel) -> List[User]:
        channel_field: Channel = await self._get_channel_field(channel_instance)
        if channel_field is None:
            return []
        channel_editors: List[User] = await self.channel_editor_repository.get_by_channel_uuid(channel_field.id)
        return channel_editors

    async def get_by_channel_uuid(self, channel_uuid: UUID) -> List[User]:
        channel_editors: List[User] = await self.channel_editor_repository.get_by_channel_uuid(channel_uuid)
        return channel_editors

    async def _get_channel_field(self, channel_instance: str | Channel) -> Channel | None:
        if isinstance(channel_instance, str):
            chat_field: Channel | None = await self.chat_service.get_by_channel_id(channel_instance)
        elif isinstance(channel_instance, Channel):
            chat_field: Channel = channel_instance
        else:
            chat_field = None
        return chat_field

    async def _get_user_field(self, user_instance: str | User) -> User | None:
        if isinstance(user_instance, str):
            user_field: User | None = await self.user_service.get_by_user_id(user_instance)
        elif isinstance(user_instance, User):
            user_field: User = user_instance
        else:
            user_field = None
        return user_field

    async def make_editor(self, channel_instance: str | Channel, user_instance: str | User) -> None:
        user_field: User | None = await self._get_user_field(user_instance)
        channel_field: Channel | None = await self._get_channel_field(channel_instance)

        if user_field is None or channel_field is None:
            return None

        channel_editors: List[User] = await self.channel_editor_repository.get_by_channel_uuid(channel_field.id)
        if user_field in channel_editors:
            return None

        await self.channel_editor_repository.create(channel_field.id, user_field.id)
        return None

    async def remove_editor(self, channel_id: UUID, user_id: UUID) -> bool:
        channel_editor = await self.channel_editor_repository.get_by_channel_and_user(channel_id, user_id)
        if channel_editor is None:
            return False
        await self.session.delete(channel_editor)
        return True
