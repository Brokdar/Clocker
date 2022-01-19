import configparser
import errno
import os
from pathlib import Path
from typing import Any, Optional

from clocker.model import parse_delta


class Settings:
    def __init__(self, file: str):
        if not Path.exists(Path(file)):
            raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), file)

        self.config = configparser.ConfigParser()
        self.config.read(file)

    def read(self, section: str, key: str) -> Any:
        """Reads a specific key from the given section.

        Args:
            section (str): config section
            key (str): config key

        Returns:
            Any: returns the configuration value if found else None
        """
        
        if section in self.config and key in self.config[section]:
            return _convert(self.config[section][key])

        return None


def _convert(value: Optional[str]) -> Any:
    if value is None:
        return None

    try:
        if value in ['true', 'false']:
            return value == 'true'

        if ':' in value:
            return parse_delta(value)

        return value

    except ValueError:
        return value
