from datetime import timedelta

import pytest
from clocker.settings import Settings


def test_read_config():
    settings = Settings('settings.ini')
    
    path = settings.read('Database', 'Path')
    pause = settings.read('Workday', 'PauseTime')
    duration = settings.read('Workday', 'Duration')

    assert path == r'P:\Python\Clocker\db'
    assert pause == timedelta(hours=0, minutes=30)
    assert duration == timedelta(hours=8, minutes=0)

def test_returns_none_if_not_found():
    settings = Settings('settings.ini')

    non_existing = settings.read('Default', 'Value')

    assert non_existing is None

def test_raise_file_not_found():
    with pytest.raises(FileNotFoundError):
        Settings('config.ini')
