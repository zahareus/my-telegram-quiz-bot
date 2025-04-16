from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command

from src.domain import ChannelService, UserService
from src.domain import session_wrap

from sqlalchemy.ext.asyncio import AsyncSession

from src.telegram.callback import ChannelCallback, WeeklyCallback, DailyCallback
from .general import _get_channel_keyboard, _get_active_keyboard

channel_router = Router()


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


@channel_router.callback_query(ChannelCallback.filter())
@session_wrap
async def handle_channel_callback(call: CallbackQuery, callback_data: ChannelCallback, session: AsyncSession):
    channel_service = ChannelService(session)
    channel_id = callback_data.channel_id
    channel_field = await channel_service.get_by_channel_id(channel_id)

    if channel_field is None:
        await call.answer("❌ Failed to find the chat.", show_alert=True)
        return

    if not channel_field.is_active:
        await call.answer("❌ This channel is disabled, you should add it first.", show_alert=True)
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



