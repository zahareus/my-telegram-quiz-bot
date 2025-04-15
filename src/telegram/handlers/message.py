from aiogram import Router
from aiogram.types import Message

from src.domain import MessageService
from config import configuration
from src.domain import session_wrap
from sqlalchemy.ext.asyncio import AsyncSession

default_router = Router()


@default_router.channel_post()
@session_wrap
async def save_message(message: Message, session: AsyncSession):
    if message.chat.id != configuration.settings.channel_id:
        return
    message_service = MessageService(session)
    await message_service.create(message=message)
