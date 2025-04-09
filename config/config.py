from dataclasses import dataclass

from .base import get_config, get_section
import configparser
from typing import List, Dict


@dataclass
class Prompt:
    system_content: str
    user_content: str

    # def __post_init__(self):
    #     self.bots_addition = int(self.bots_addition)

@dataclass
class Settings:
    channel_name: str
    date_format: str
    channel_id: int
    default_tz: str
    update_text: str


@dataclass
class SkipParts:
    parts: str | List[str]

    def __post_init__(self):
        self.parts = [i for i in self.parts.split(",")]


@dataclass
class EmojiMap:
    map: Dict[str, str]


@dataclass
class Config:
    prompt: Prompt
    emoji_map: EmojiMap
    settings: Settings
    skip: SkipParts


def load_config():
    configuration_file = configparser.ConfigParser()
    configuration_file.read("config.ini", encoding="utf-8")

    local_config = Config(
        prompt=Prompt(
            system_content=get_config(configuration_file, "system_content", "PROMPT", default=""),
            user_content=get_config(configuration_file, "user_content", "PROMPT", default="")
        ),
        emoji_map=EmojiMap(
            map=get_section(configuration_file, "EMOJI_MAP")
        ),
        settings=Settings(
            channel_name=get_config(configuration_file, "channel_name", "SETTINGS", default=""),
            date_format=get_config(configuration_file, "date_format", "SETTINGS", default="%Y-%m-%d"),
            channel_id=int(get_config(configuration_file, "channel_id", "SETTINGS")),
            default_tz=get_config(configuration_file, "default_tz", "SETTINGS"),
            update_text=get_config(configuration_file, "update_text", "SETTINGS")
        ),
        skip=SkipParts(
            parts=get_config(configuration_file, "skip_parts", "SKIP_PARTS", default="")
        )
    )
    return local_config


configuration: Config = load_config()
