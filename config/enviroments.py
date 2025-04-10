import logging
import sys
import threading
from dataclasses import dataclass
from os.path import join
from dotenv import load_dotenv

from .base import get_environ, get_project_root


@dataclass
class Telegram:
    bot_token: str


@dataclass
class Database:
    host: str
    name: str
    port: int
    type: str
    user: str
    password: str
    url: str = None

    def process_url(self):
        self.url = f"{self.type}+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"


@dataclass
class AiModel:
    token: str


@dataclass
class Environ:
    telegram: Telegram
    database: Database
    model: AiModel
    dev_mode: bool


def set_logging_config():
    logging.basicConfig(
        filename="./.local/logger.log",
        filemode='a',
        format='%(asctime)s,%(msecs)d - %(name)s - %(levelname)s: %(message)s',
        datefmt='%H:%M:%S',
        level=logging.INFO
    )

    def custom_err_handler(arg1, arg2=None, arg3=None):
        if type(arg1) is threading.ExceptHookArgs:
            exc_type = arg1.exc_type
            exc_value = arg1.exc_value
            exc_traceback = arg1.exc_traceback
        else:
            exc_type = arg1
            exc_value = arg2
            exc_traceback = arg3

        logging.exception("Uncaught exception :", exc_info=(exc_type, exc_value, exc_traceback))
    sys.excepthook = custom_err_handler


def load_environ() -> Environ:
    set_logging_config()
    dotenv_path = join(get_project_root(), '.env')
    load_dotenv(dotenv_path)
    local_config = Environ(
        telegram=Telegram(
            bot_token=get_environ('BOT_TOKEN'),
        ),
        database=Database(
            host=get_environ('DB_HOST', default='localhost'),
            name=get_environ('DB_NAME', default='summarize_dev'),
            port=int(get_environ('DB_PORT', default=5432)),
            type=get_environ('DB_TYPE', default='postgresql'),
            user=get_environ('DB_USER', default='postgres'),
            password=get_environ('DB_PASSWORD', default='pgAdminPassword')
        ),
        model=AiModel(
            token=get_environ('GEMINI_TOKEN')
        ),
        dev_mode=bool(int(get_environ('DEV_MODE', default=1)))
    )
    local_config.database.process_url()
    return local_config


environments: Environ = load_environ()
