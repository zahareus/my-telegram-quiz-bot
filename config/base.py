import os
from os.path import dirname
import configparser
from typing import Dict


class ImproperlyConfigured(Exception):
    """Raises when a environment variable is missing."""

    def __init__(self, variable_name: str, *args):
        self.variable_name = variable_name
        self.message = f"{variable_name} environment variable is unset. Set to proceed."
        super().__init__(self.message, *args)


def get_project_root() -> str:
    """Get the project root."""
    return dirname(dirname(__file__))


def get_config(config: configparser.ConfigParser, variable_name: str, section: str, default=None):
    """Get the configuration variable or raise an error."""
    try:
        return config[section][variable_name]
    except KeyError:
        if default:
            return default
        raise ImproperlyConfigured(variable_name)

def get_section(config: configparser.ConfigParser, section: str) -> Dict[str, str]:
    """Get the configuration section or raise an error."""
    try:
        return dict(config[section])
    except KeyError:
        raise ImproperlyConfigured(section)


def get_environ(variable_name: str, default=None) -> str:
    """Get the environment variable or raise an error."""
    try:
        return os.environ[variable_name]
    except KeyError:
        if default:
            return default
        raise ImproperlyConfigured(variable_name)
