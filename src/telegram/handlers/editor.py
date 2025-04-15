from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardMarkup
from aiogram.types import Message, KeyboardButtonRequestUser, ReplyKeyboardRemove
from aiogram.utils.keyboard import ReplyKeyboardBuilder, ReplyKeyboardMarkup

from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from src.domain import ChannelService, UserService, ChannelEditorService
from src.domain import session_wrap

from src.database import Channel, User
from sqlalchemy.ext.asyncio import AsyncSession

from typing import List
from src.telegram.callback import (EditorCallback, SelectEditorCallback, AddEditorCallback, CancelCallback,
                                   RemoveEditorCallback)

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
        text="Cancel",
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


def _get_editor_remove_keyboard(channel_id: str, editor: User) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(
        text=f"Remove",
        callback_data=RemoveEditorCallback(channel_id=channel_id, user_id=editor.user_id).pack()
    )
    builder.button(
        text="Cancel",
        callback_data=CancelCallback().pack()
    )
    builder.adjust(1)
    return builder.as_markup()


@editor_router.callback_query(SelectEditorCallback.filter())
@session_wrap
async def select_editor_callback(call: CallbackQuery, callback_data: SelectEditorCallback, session: AsyncSession):
    user_service = UserService(session)
    channel_service = ChannelService(session)

    if not await user_service.is_admin(call.message):
        await call.answer("You are not an admin.", show_alert=True)
        return

    channel_field: Channel = await channel_service.get_by_channel_id(callback_data.channel_id)
    if channel_field is None:
        await call.answer("❌ Failed to get the chat.")
        return

    editor_field: User = await user_service.get_by_user_id(callback_data.user_id)
    if editor_field is None:
        await call.answer("❌ Failed to get the editor.")
        return

    await call.answer()

    reply_markup = _get_editor_remove_keyboard(channel_field.channel_id, editor_field)
    await call.message.answer(f"Selected editor: @{editor_field.username or editor_field.user_id}",
                              reply_markup=reply_markup)


def _get_user_keyboard() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.button(
        text="📥 Share User",
        request_user=KeyboardButtonRequestUser(
            request_id=1,
            user_is_bot=False
        )
    )
    builder.adjust(1)
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=True)


class AddEditorStates(StatesGroup):
    waiting_for_user = State()


@editor_router.callback_query(AddEditorCallback.filter())
@session_wrap
async def add_editor_callback(call: CallbackQuery, callback_data: AddEditorCallback, session: AsyncSession,
                              state: FSMContext):
    user_service = UserService(session)
    channel_service = ChannelService(session)

    if not await user_service.is_admin(call.message):
        await call.answer("You are not an admin.", show_alert=True)
        return

    channel_field: Channel = await channel_service.get_by_channel_id(callback_data.channel_id)
    if channel_field is None:
        await call.answer("❌ Failed to get the chat.")
        return

    await state.set_state(AddEditorStates.waiting_for_user)
    await state.update_data(channel_id=callback_data.channel_id)
    await call.message.answer(
        "📥 Please, share user, u want to add as editor",
        reply_markup=_get_user_keyboard()
    )
    await call.answer()


@editor_router.message(AddEditorStates.waiting_for_user, lambda message: message.user_shared is not None)
@session_wrap
async def process_shared_user(message: Message, session: AsyncSession, state: FSMContext) -> None:
    shared_user_id = message.user_shared.user_id

    user_service = UserService(session)
    editor_service = ChannelEditorService(session)
    channel_service = ChannelService(session)

    data = await state.get_data()
    channel_id: str | None = data.get("channel_id", None)

    if channel_id is None:
        await message.answer("❌ No active channel context found. Try again.")
        await state.clear()
        return

    user_field = await user_service.get_or_create_user(str(shared_user_id))
    channel_field = await channel_service.get_by_channel_id(channel_id)
    if channel_field is None or user_field is None:
        await message.answer("❌ Failed to get the chat or user.")
        await state.clear()
        return

    await editor_service.make_editor(channel_field, user_field)
    await message.answer(
        f"✅ User <b>{user_field.username or shared_user_id}</b> added as editor to <b>{channel_field.channel_title or 'Untitled'}</b>.\nUser details will be updated once user starts the bot.",
        reply_markup=ReplyKeyboardRemove(),
        parse_mode="HTML"
    )

    await state.clear()


@editor_router.callback_query(RemoveEditorCallback.filter())
@session_wrap
async def remove_editor_callback(call: CallbackQuery, callback_data: RemoveEditorCallback, session: AsyncSession):
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

    editor_field: User = await user_service.get_by_user_id(callback_data.user_id)
    if editor_field is None:
        await call.answer("❌ Failed to get the editor.")
        return

    await call.answer()

    status = await channel_editor_service.remove_editor(channel_field.id, editor_field.id)
    if not status:
        await call.answer(f"❌ Editor @{editor_field.username or editor_field.user_id} not found in {channel_field.channel_title or 'Untitled'} chat.", show_alert=True)
        await call.message.delete()
        return
    await call.message.answer(f"✅ Editor @{editor_field.username or editor_field.user_id} removed from {channel_field.channel_title or 'Untitled'} chat.")
