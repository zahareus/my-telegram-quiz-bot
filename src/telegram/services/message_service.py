import logging
import time

from typing import List
from src.database import MessageRepository
from config import configuration, environments
import datetime

from sqlalchemy.ext.asyncio import AsyncSession

import requests
import json


class MessageService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.message_repository = MessageRepository(session)
        self.logger = logging.getLogger(__name__)

    async def get_past_day_messages(self, channel_id: str) -> List[List[str]]:
        yesterday_time = datetime.datetime.now(tz=None) - datetime.timedelta(days=1)
        messages_list = await self.message_repository.get_by_chat_id(
            chat_id=channel_id,
            all_after=yesterday_time
        )
        messages_text = []
        for message in messages_list:
            if message.message_text is None:
                continue
            is_skip = False
            for skip_part in configuration.skip.parts:
                if skip_part in message.message_text:
                    is_skip = True
                    break
            if is_skip:
                continue

            message_link = f"https://t.me/c/{str(channel_id)[4:]}/{message.message_id}"
            messages_text.append([str(message.message_text), message_link])
        return messages_text

    # @staticmethod
    # async def get_relevant_emoji(text: str) -> str:
    #     if text is not None:
    #         text = text.lower()
    #         for keyword, emoji in configuration.emoji_map.map.items():
    #             if keyword in text:
    #                 return emoji
    #     return "📰"

    def summarize_text(self, text: str) -> str | None:
        # time.sleep(5)
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {environments.model.token}",
            },
            data=json.dumps({
                "model": "google/gemini-2.0-flash-exp:free",
                "messages": [
                    {
                        "role": "system",
                        "content": [
                            {
                                "type": "text",
                                "text": configuration.prompt.system_content.format(emoji=configuration.emoji_map.map),
                            }
                        ]
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": configuration.prompt.user_content.format(text=text),
                            }
                        ]
                    }
                ]
            })
        )

        try:
            content = response.json()["choices"][0]["message"]["content"]
            return content
        except KeyError:
            self.logger.error(f"Error in response format from OpenRouter API, response: {response.json()}")
            return None

    # async def get_user(self) -> User:
    #     if self.user_field is None:
    #         await self.init_user()
    #     return self.user_field
    #
    # async def check_permission(self, name: str):
    #     if self.user_field is None:
    #         await self.init_user()
    #
    #     if not await self.role_repository.check_permission(self.user_field.role, name):
    #         raise NotEnoughPermissionsException
    #
    # async def check_timeout(self, timeout_seconds: int):
    #     if self.user_field is None:
    #         await self.init_user()
    #
    #     last_suggestion = await self.suggestion_repository.get_last(self.user_field)
    #     if last_suggestion is None:
    #         return
    #     if not await self.suggestion_repository.check_timeout(last_suggestion, timeout_seconds):
    #         raise UserTimeoutException
    #
    # async def get_admins_chat_id(self) -> list[str]:
    #     admins = await self.user_repository.get_by_role(await self.role_repository.get_by_name("admin"))
    #     return [admin.chat_id for admin in admins]
