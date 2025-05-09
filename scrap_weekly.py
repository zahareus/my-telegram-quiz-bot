from pyexpat.errors import messages

from src.database import User
from src.domain.service import MessageService, ChannelEditorService, ChannelService
from src.domain import session_wrap
import logging
from src.telegram import bot
import asyncio
from config import configuration
from typing import List
import datetime
from sqlalchemy.ext.asyncio import AsyncSession


@session_wrap
async def get_info(session: AsyncSession):
    message_service: MessageService = MessageService(session)
    editor_service: ChannelEditorService = ChannelEditorService(session)
    channel_service = ChannelService(session)

    for channel_field in await channel_service.get_weekly():
        logging.info(f"Scrap weekly update for {channel_field.channel_title or 'Unknown channel'}")
        channel_id = channel_field.channel_id
        messages_list: List[List[str]] = await message_service.get_past_messages(str(channel_id), days=7)
        if len(messages_list) == 0:
            continue
        summary_text: str = "\n".join([f"[link: {link}]\n{text}\n" for text, link in messages_list])
        summary_text: str = message_service.summarize_text(summary_text)

        summary_result = configuration.settings.weekly_text + "\n\n" + summary_text
        logging.info(f"Weekly update done for {channel_field.channel_title or 'Unknown channel'}:\n{summary_result}")

        user_fields: List[User] = await editor_service.get_by_channel(channel_field)
        try:
            for user_field in user_fields:
                await bot.send_message(user_field.user_id,
                                       f"🔄 Weekly update for {channel_field.channel_title or 'Unknown channel'}")
                await bot.send_message(user_field.user_id, summary_result)
        except Exception as e:
            logging.error(f"Failed to send message:\n{summary_result}\nWith error: {e}")
            continue
        await asyncio.sleep(60)


if __name__ == "__main__":
    logging.info("Weekly scrap update")
    asyncio.run(get_info())
