import logging
from src.database import UserRepository, User
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.types import Message


class UserService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.user_repository = UserRepository(session)
        self.logger = logging.getLogger(__name__)

    @staticmethod
    async def check_chat(message: Message) -> bool:
        return message.chat.type == 'private'

    async def get_user(self, message: Message) -> User | None:
        if not await self.check_chat(message):
            return None
        user_field = await self.user_repository.get_by_user_id(str(message.chat.id))
        if user_field is None:
            username = None
            if message.chat.username:
                username = message.chat.username
            elif message.chat.title:
                username = message.chat.title
            user_field = await self.user_repository.create(
                user_id=str(message.chat.id),
                username=username
            )
        else:
            if user_field.username is None:
                if message.chat.username:
                    user_field.username = message.chat.username
                elif message.chat.title:
                    user_field.username = message.chat.title
        return user_field

    async def get_admins_ids(self):
        return [user_field.user_id for user_field in await self.user_repository.get_admins()]

    async def is_admin(self, message: Message) -> bool:
        user_field = await self.get_user(message)
        if user_field is None:
            return False
        return user_field.is_admin

    async def get_by_user_id(self, user_id: str) -> User | None:
        user_field = await self.user_repository.get_by_user_id(user_id)
        return user_field

    async def get_or_create_user(self, user_id: str) -> User | None:
        user_field = await self.user_repository.get_by_user_id(user_id)
        if user_field is None:
            user_field = await self.user_repository.create(
                user_id=user_id,
                username=None
            )
        return user_field
