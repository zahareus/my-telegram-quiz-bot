from aiogram import Router
from aiogram.types import Message

from domain import ChannelService
from src.domain import MessageService
from config import configuration
from src.domain import session_wrap
from sqlalchemy.ext.asyncio import AsyncSession

default_router = Router()


@default_router.channel_post()
@session_wrap
async def save_message(message: Message, session: AsyncSession):
    channel_service = ChannelService(session)
    active_channels = await channel_service.get_active()
    if str(message.chat.id) not in [channel_field.channel_id for channel_field in active_channels]:
        return
    message_service = MessageService(session)
    await message_service.create(message=message)
