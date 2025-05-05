from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardMarkup
from src.database import Channel
from src.telegram.callback import (ChannelCallback, WeeklyCallback, DailyCallback, DeactivateCallback, CancelCallback,
                                   EditorCallback)
from typing import List


def _get_active_keyboard(active_channels: List[Channel]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    for channel in active_channels:
        title = channel.channel_title or "Untitled Chat"
        builder.button(text=f"💬 {title}", callback_data=ChannelCallback(channel_id=channel.channel_id).pack())
    builder.adjust(1)
    return builder.as_markup()


def _get_channel_keyboard(channel_field: Channel) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(
        text="👥 Change editors",
        callback_data=EditorCallback(channel_id=channel_field.channel_id).pack()
    )
    # builder.button(
    #     text=("✅ " if channel_field.is_daily else "❎ ") + "Daily",
    #     callback_data=DailyCallback(channel_id=channel_field.channel_id, is_daily=not channel_field.is_daily).pack()
    # )
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
