from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardMarkup
from aiogram.filters import Command

from src.domain import ChannelService, UserService
from src.domain import session_wrap

from src.database import Channel
from sqlalchemy.ext.asyncio import AsyncSession

from typing import List
from src.telegram.callback import (ChannelCallback, WeeklyCallback, DailyCallback, DeactivateCallback, CancelCallback,
                                   EditorCallback)

channel_router = Router()


def _get_active_keyboard(active_channels: List[Channel]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    for channel in active_channels:
        title = channel.channel_title or "Untitled Chat"
        builder.button(text=f"💬 {title}", callback_data=ChannelCallback(channel_id=channel.channel_id).pack())
    builder.adjust(1)
    return builder.as_markup()


@channel_router.message(Command("channel"), F.chat.type == "private")
@session_wrap
async def select_channel(message: Message, session: AsyncSession):
    user_service = UserService(session)
    channel_service = ChannelService(session)

    if not await user_service.is_admin(message):
        await message.answer("You are not an admin.")
        return

    active_channels = await channel_service.get_active()
    reply_markup = _get_active_keyboard(active_channels)
    if len(active_channels) == 0:
        await message.answer("❌ No active channels found.\nPress /share to add a channel.")
        return
    await message.answer("Click the button to manage the channel", reply_markup=reply_markup)


def _get_channel_keyboard(channel_field: Channel) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(
        text="👥 Change editors",
        callback_data=EditorCallback(channel_id=channel_field.channel_id).pack()
    )
    builder.button(
        text=("✅ " if channel_field.is_daily else "❎ ") + "Daily",
        callback_data=DailyCallback(channel_id=channel_field.channel_id, is_daily=not channel_field.is_daily).pack()
    )
    builder.button(
        text=("✅ " if channel_field.is_weekly else "❎ ") + "Weekly",
        callback_data=WeeklyCallback(channel_id=channel_field.channel_id, is_weekly=not channel_field.is_weekly).pack()
    )
    builder.button(
        text="❌ Remove channel",
        callback_data=DeactivateCallback(channel_id=channel_field.channel_id).pack()
    )
    builder.button(
        text="🔙 Back",
        callback_data=CancelCallback().pack()
    )
    builder.adjust(1)
    return builder.as_markup()


@channel_router.callback_query(ChannelCallback.filter())
@session_wrap
async def handle_channel_callback(call: CallbackQuery, callback_data: ChannelCallback, session: AsyncSession):
    channel_service = ChannelService(session)
    channel_id = callback_data.channel_id
    channel_field = await channel_service.get_by_channel_id(channel_id)

    if channel_field is None:
        await call.answer("❌ Failed to find the chat.", show_alert=True)
        return

    await call.message.answer(
        f"💬 {channel_field.channel_title or 'Untitled Chat'} settings",
        reply_markup=_get_channel_keyboard(channel_field)
    )
    await call.answer()


@channel_router.callback_query(DailyCallback.filter())
@session_wrap
async def handle_daily_callback(call: CallbackQuery, callback_data: DailyCallback, session: AsyncSession):
    channel_service = ChannelService(session)
    channel_id = callback_data.channel_id
    is_daily = callback_data.is_daily
    channel_field = await channel_service.get_by_channel_id(channel_id)

    if channel_field is None:
        await call.answer("❌ Failed to find the chat.", show_alert=True)
        return

    channel_field.is_daily = is_daily

    await call.answer(
        f"✅ Daily notifications {'enabled' if is_daily else 'disabled'} for {channel_field.channel_title or 'Untitled Chat'}"
    )
    await call.message.edit_reply_markup(reply_markup=_get_channel_keyboard(channel_field))


@channel_router.callback_query(WeeklyCallback.filter())
@session_wrap
async def handle_weekly_callback(call: CallbackQuery, callback_data: WeeklyCallback, session: AsyncSession):
    channel_service = ChannelService(session)
    channel_id = callback_data.channel_id
    is_weekly = callback_data.is_weekly
    channel_field = await channel_service.get_by_channel_id(channel_id)

    if channel_field is None:
        await call.answer("❌ Failed to find the chat.", show_alert=True)
        return

    channel_field.is_weekly = is_weekly

    await call.answer(
        f"✅ Weekly notifications {'enabled' if is_weekly else 'disabled'} for {channel_field.channel_title or 'Untitled Chat'}"
    )
    await call.message.edit_reply_markup(reply_markup=_get_channel_keyboard(channel_field))


@channel_router.callback_query(DeactivateCallback.filter())
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

