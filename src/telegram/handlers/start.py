from aiogram import Router
from aiogram.types import Message

from src.domain import UserService
from src.domain import session_wrap
from aiogram.filters import CommandStart
from sqlalchemy.ext.asyncio import AsyncSession

start_router = Router()


@start_router.message(CommandStart())
@session_wrap
async def start_message(message: Message, session: AsyncSession):
    user_service = UserService(session)
    await user_service.get_user(message=message)
    await message.reply("Hello! I'm a bot!")


@start_router.message()
@session_wrap
async def default_message(message: Message, session: AsyncSession):
    user_service = UserService(session)
    await user_service.get_user(message=message)
    await message.reply("There's no functional tools yet.")
