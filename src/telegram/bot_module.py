from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from config import environments
from .handlers import *

bot: Bot = Bot(token=environments.telegram.bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp: Dispatcher = Dispatcher()

dp.include_router(start_router)
dp.include_router(default_router)
