from aiogram import Router
from aiogram.types import Message

from src.domain import UserService, session_wrap
from sqlalchemy.ext.asyncio import AsyncSession

default_router = Router()


@default_router.message()
@session_wrap
async def default_message(message: Message, session: AsyncSession):
    user_service = UserService(session)
    await user_service.get_user(message=message)

