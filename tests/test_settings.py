from datetime import timedelta

import pytest
from clocker.settings import Settings


def test_read_config():
    settings = Settings('tests/settings.ini')

    path = settings.read('Database', 'Path')
    pause = settings.read('Work', 'DefaultPauseTime')
    duration = settings.read('Work', 'WorkingHours')
    vacation_days = settings.read('Work', 'VacationDays')

    assert path == r'db'
    assert pause == timedelta(hours=1)
    assert duration == timedelta(hours=8, minutes=0)
    assert vacation_days == 30


def test_returns_none_if_not_found():
    settings = Settings('settings.ini')

    non_existing = settings.read('Default', 'Value')

    assert non_existing is None


def test_raise_file_not_found():
    with pytest.raises(FileNotFoundError):
        Settings('config.ini')
