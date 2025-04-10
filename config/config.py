from dataclasses import dataclass

from .base import get_config, get_section
import configparser
from typing import List, Dict
from . import environments


@dataclass
class Prompt:
    system_content: str
    user_content: str

    # def __post_init__(self):
    #     self.bots_addition = int(self.bots_addition)


@dataclass
class Settings:
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


def merge_ini_files(file1_path: str, file2_path: str) -> configparser.ConfigParser:
    merged_config = configparser.ConfigParser()
    merged_config.read(file1_path, encoding="utf-8")

    temp_config = configparser.ConfigParser()
    temp_config.read(file2_path, encoding="utf-8")

    for section in temp_config.sections():
        if not merged_config.has_section(section):
            merged_config.add_section(section)
        for key, value in temp_config.items(section):
            merged_config.set(section, key, value)
    return merged_config


def load_config():
    dev_mode = environments.dev_mode
    additional_config = "develop.ini" if dev_mode else "production.ini"
    configuration_file = merge_ini_files("global.ini", additional_config)

    local_config = Config(
        prompt=Prompt(
            system_content=get_config(configuration_file, "system_content", "PROMPT", default=""),
            user_content=get_config(configuration_file, "user_content", "PROMPT", default="")
        ),
        emoji_map=EmojiMap(
            map=get_section(configuration_file, "EMOJI_MAP")
        ),
        settings=Settings(
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
