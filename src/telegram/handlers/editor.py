from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardMarkup
from aiogram.filters import Command

from src.domain import ChannelService, UserService, ChannelEditorService
from src.domain import session_wrap

from src.database import Channel, User
from sqlalchemy.ext.asyncio import AsyncSession

from typing import List
from src.telegram.callback import (EditorCallback, SelectEditorCallback, AddEditorCallback, CancelCallback)

editor_router = Router()


def _get_editors_keyboard(channel_id: str, editors_list: List[User]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for editor in editors_list:
        builder.button(text=f"@{editor.username or editor.user_id}",
                       callback_data=SelectEditorCallback(channel_id=channel_id, user_id=editor.user_id).pack())
    builder.button(
        text="➕ Add editor",
        callback_data=AddEditorCallback(channel_id=channel_id).pack()
    )
    builder.button(
        text="❌ Cancel",
        callback_data=CancelCallback().pack()
    )
    builder.adjust(1)
    return builder.as_markup()


@editor_router.callback_query(EditorCallback.filter())
@session_wrap
async def editor_callback(call: CallbackQuery, callback_data: EditorCallback, session: AsyncSession):
    user_service = UserService(session)
    channel_service = ChannelService(session)
    channel_editor_service = ChannelEditorService(session)

    if not await user_service.is_admin(call.message):
        await call.answer("You are not an admin.", show_alert=True)
        return

    channel_field: Channel = await channel_service.get_by_channel_id(callback_data.channel_id)
    if channel_field is None:
        await call.answer("❌ Failed to get the chat.")
        return

    await call.answer()

    editors: List[User] = await channel_editor_service.get_by_channel_uuid(channel_field.id)
    reply_markup = _get_editors_keyboard(channel_field.channel_id, editors)
    if len(editors) == 0:
        await call.message.answer("No editors found.", reply_markup=reply_markup)
        return

    await call.message.answer("Select editor to remove or add new editor", reply_markup=reply_markup)
