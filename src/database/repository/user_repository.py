from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import User
from uuid import UUID
import logging
from typing import List


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.logger = logging.getLogger(__name__)

    async def get_by_uuid(self, user_id: UUID) -> User | None:
        stmt = select(User).where(User.id == user_id).limit(1)
        return await self.session.scalar(stmt)

    async def get_by_username(self, username: str) -> User | None:
        stmt = select(User).where(User.username == username).limit(1)
        return await self.session.scalar(stmt)

    async def get_by_user_id(self, user_id: str) -> User | None:
        stmt = select(User).where(User.user_id == user_id).limit(1)
        return await self.session.scalar(stmt)

    async def create(self, user_id: str, username: str = None) -> User:
        user = User(user_id=user_id,
                    username=username)
        self.session.add(user)
        await self.session.flush()
        self.logger.info(f"User {user.id} created (chat_id: {user.user_id}, username: {user.username}), id: {user.id}")
        return await self.get_by_uuid(user.id)

    @staticmethod
    async def check_admin(user: User) -> bool:
        return user.is_admin

    async def get_admins(self) -> List[User]:
        stmt = select(User).where(User.is_admin == True)
        return list(await self.session.scalars(stmt))

    async def get_all(self) -> List[User]:
        stmt = select(User)
        return list(await self.session.scalars(stmt))
