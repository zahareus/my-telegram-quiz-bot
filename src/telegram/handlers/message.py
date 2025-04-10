from aiogram import Router
from aiogram.types import Message

from src.database import sessionmanager
from src.database import MessageRepository
from config import configuration

default_router = Router()


@default_router.message()
@default_router.channel_post()
async def save_message(message: Message):
    if message.chat.id != configuration.settings.channel_id:
        return

    if message.text is None and message.caption is None:
        return

    message_text = message.text
    if message_text is None:
        message_text = message.caption

    async with sessionmanager.session() as session:
        text_repo = MessageRepository(session)

        await text_repo.create(chat_id=str(message.chat.id),
                               message_id=str(message.message_id),
                               message_text=message_text,
                               timestamp=message.date)
        await session.commit()