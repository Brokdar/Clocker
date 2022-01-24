import configparser
import errno
import os
from pathlib import Path
from typing import Any

from clocker import converter


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
            return converter.str_to_value(self.config[section][key])

        return None
