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

    for channel_field in await channel_service.get_daily():
        channel_id = channel_field.channel_id
        messages_list: List[List[str]] = await message_service.get_past_day_messages(str(channel_id))
        summary_text: str = "\n".join([f"[post]\n[link: {link}]\n{text}\n" for text, link in messages_list])
        summary_text: str = message_service.summarize_text(summary_text)

        # summary_texts: List[str] = [f'{text} (<a href = "{link}">посилання</a>)' for text, link in summary_list]
        yesterday_data = (datetime.datetime.now(tz=None) - datetime.timedelta(days=1)).date()
        summary_result = configuration.settings.update_text.format(
            yesterday_date=yesterday_data) + "\n\n" + summary_text

        user_fields: List[User] = await editor_service.get_by_channel(channel_field)
        for user_field in user_fields:
            await bot.send_message(user_field.user_id,
                                   f"🔄 Daily update for {channel_field.channel_title or 'Unknown channel'}")
            await bot.send_message(user_field.user_id, summary_result)


if __name__ == "__main__":
    logging.info("Scrap update")
    asyncio.run(get_info())
