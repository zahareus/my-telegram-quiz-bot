from aiogram import Router
from aiogram.types import Message, KeyboardButton, KeyboardButtonRequestUser, KeyboardButtonRequestChat
from aiogram.utils.keyboard import ReplyKeyboardBuilder, ReplyKeyboardMarkup

from src.domain import UserService
from src.domain import session_wrap
from aiogram.filters import Command, CommandStart
from sqlalchemy.ext.asyncio import AsyncSession

start_router = Router()


@start_router.message(CommandStart())
@session_wrap
async def start_message(message: Message, session: AsyncSession):
    user_service = UserService(session)
    await user_service.get_user(message=message)
    await message.reply("Hello! I'm a bot!")


# @start_router.message()
# @session_wrap
# async def default_message(message: Message, session: AsyncSession):
#     user_service = UserService(session)
#     await user_service.get_user(message=message)
#     await message.reply("There's no functional tools yet.")
# def get_request_keyboard() -> ReplyKeyboardMarkup:
#     builder = ReplyKeyboardBuilder()
#
#     builder.button(
#         text="📥 Share User",
#         request_user=KeyboardButtonRequestUser(
#             request_id=1,
#             user_is_bot=False
#         )
#     )
#
#     builder.button(
#         text="👥 Share Chat",
#         request_chat=KeyboardButtonRequestChat(
#             request_id=2,
#             chat_is_channel=True
#         )
#     )
#
#     # Adjust layout (e.g., two buttons in a row)
#     builder.adjust(2)
#     return builder.as_markup(resize_keyboard=True, one_time_keyboard=True)
#
# @start_router.message(Command("hello"))
# async def hello_message(message: Message):
#     keyboard = get_request_keyboard()
#     await message.answer("Choose what you'd like to share:", reply_markup=keyboard)
