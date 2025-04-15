from aiogram import Router, F
from aiogram.types import Message, KeyboardButtonRequestChat
from aiogram.utils.keyboard import ReplyKeyboardBuilder, ReplyKeyboardMarkup
from aiogram.filters import Command

from src.domain import ChannelService, UserService
from src.domain import session_wrap

from sqlalchemy.ext.asyncio import AsyncSession

share_router = Router()

def _get_share_keyboard() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()

    builder.button(
        text="👥 Share Chat",
        request_chat=KeyboardButtonRequestChat(
            request_id=2,
            chat_is_channel=True,
            request_title=True
        )
    )
    builder.adjust(1)
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=True)

@share_router.message(Command("share"), F.chat.type == "private")
@session_wrap
async def add_channel(message: Message, session: AsyncSession):
    user_service = UserService(session)

    if not await user_service.is_admin(message):
        await message.answer("You are not an admin.")
        return

    keyboard = _get_share_keyboard()
    await message.answer("Click the button to add channel", reply_markup=keyboard)


@share_router.message(lambda message: message.chat_shared is not None)
@session_wrap
async def handle_channel_shared(message: Message, session: AsyncSession):
    channel_service = ChannelService(session)
    channel_id = message.chat_shared.chat_id
    title = message.chat_shared.title

    chat_field = await channel_service.get_or_create_id(channel_id=str(channel_id), title=title)

    await channel_service.set_active(chat_field, is_active=True)
    if chat_field is None:
        await message.answer("❌ Failed to add the chat.")
        return
    await message.answer(f"✅ You added the chat: {title}.")