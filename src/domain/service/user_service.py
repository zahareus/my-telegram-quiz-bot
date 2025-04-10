import logging
from src.database import UserRepository, User
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.types import Message


class UserService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.user_repository = UserRepository(session)
        self.logger = logging.getLogger(__name__)

    async def get_user(self, message: Message) -> User:
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
        return user_field
