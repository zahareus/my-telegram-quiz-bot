from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardMarkup

from src.domain import ChannelService, UserService
from src.domain import session_wrap

from sqlalchemy.ext.asyncio import AsyncSession

from src.telegram.callback import DeactivateCallback, ConfirmDeactivateCallback, CancelCallback
from .general import _get_channel_keyboard, _get_active_keyboard

deactivate_router = Router()


def _confirm_deactivation_keyboard(channel_id: str):
    builder = InlineKeyboardBuilder()
    builder.button(
        text="✅ Approve",
        callback_data=ConfirmDeactivateCallback(channel_id=channel_id).pack()
    )
    builder.button(
        text="❌ Cancel",
        callback_data=CancelCallback().pack()
    )
    return builder.as_markup()


@deactivate_router.callback_query(DeactivateCallback.filter())
async def confirm_deactivation(call: CallbackQuery, callback_data: DeactivateCallback):
    channel_id = callback_data.channel_id
    reply_markup = _confirm_deactivation_keyboard(channel_id)
    await call.message.edit_text(
        "Are you sure you want to deactivate this channel?",
        reply_markup=reply_markup
    )
    await call.answer()


@deactivate_router.callback_query(ConfirmDeactivateCallback.filter())
@session_wrap
async def handle_deactivate_callback(call: CallbackQuery, callback_data: DeactivateCallback, session: AsyncSession):
    channel_service = ChannelService(session)
    channel_id = callback_data.channel_id
    channel_field = await channel_service.get_by_channel_id(channel_id)

    if channel_field is None:
        await call.answer("❌ Failed to find the chat.", show_alert=True)
        return

    await channel_service.set_active(channel_field, is_active=False)
    await call.answer(f"❌ Removed {channel_field.channel_title or 'Untitled Chat'} from active channels.")
    await call.message.delete()

    active_channels = await channel_service.get_active()
    reply_markup = _get_active_keyboard(active_channels)
    if len(active_channels) == 0:
        await call.message.answer("❌ No active channels found.\nPress /share to add a channel.")
        return
    await call.message.answer("Click the button to add channel", reply_markup=reply_markup)
