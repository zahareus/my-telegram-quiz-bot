from src.database import sessionmanager
from src.telegram.services import MessageService
import logging
from src.telegram import bot
import asyncio
from config import configuration
from typing import List
import datetime

async def get_info():
    async with sessionmanager.session() as session:
        static_service: MessageService = MessageService(session)
        channel_id = configuration.settings.channel_id
        messages_list: List[List[str]] = await static_service.get_past_day_messages(str(channel_id))
        summary_text: str = "\n".join([f"[post]\n[link: {link}]\n{text}\n" for text, link in messages_list])
        summary_text: str = static_service.summarize_text(summary_text)

        # summary_texts: List[str] = [f'{text} (<a href = "{link}">посилання</a>)' for text, link in summary_list]
        yesterday_data = (datetime.datetime.now(tz=None) - datetime.timedelta(days=1)).date()
        summary_result = configuration.settings.update_text.format(yesterday_date=yesterday_data) + "\n\n" + summary_text
        await bot.send_message(channel_id, summary_result)

if __name__ == "__main__":
    logging.info("Scrap update")
    asyncio.run(get_info())