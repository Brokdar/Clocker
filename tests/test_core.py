from datetime import datetime, time, timedelta
from time import sleep
from typing import Tuple

import pytest
from clocker.core import Tracker, round_next_quarter, round_prev_quarter
from clocker.database import Database
from clocker.settings import Settings

from tests import db


def setup() -> Tuple[Database, Tracker]:
    file = 'tests/settings.ini'
    database = db.get()
    tracker = Tracker(Settings(file), database)

    return database, tracker


def test_start_tracking():
    database, tracker = setup()
    today = datetime.now().date()
    result = database.load(today)

    if result is not None:
        database.remove(today)

    tracker.start()

    result = database.load(today)
    assert result
    assert result.date == today
    assert result.begin is not None
    assert result.end is None
    assert result.pause is not None


def test_start_does_not_update_already_existing_records():
    database, tracker = setup()
    today = datetime.now().date()
    result = database.load(today)

    if result is not None:
        database.remove(today)

    tracker.start()
    workday = database.load(today)

    sleep(3)
    tracker.start()

    result = database.load(today)
    assert result
    assert workday.begin == result.begin


def test_stop_tracking():
    database, tracker = setup()
    today = datetime.now().date()

    tracker.start()
    result = database.load(today)
    assert result

    tracker.stop()

    result = database.load(today)
    assert result
    assert result.date == today
    assert result.begin is not None
    assert result.end is not None
    assert result.pause is not None


def test_track_manually():
    database, tracker = setup()
    today = datetime.now().date()
    begin = time(8, 0)
    end = time(16, 30)
    pause = timedelta(minutes=30)
    tracker.track(today, begin, end, pause)

    result = database.load(today)
    assert result
    assert result.date == today
    assert result.begin == begin
    assert result.end == end
    assert result.pause == pause


def test_update_start_time():
    database, tracker = setup()
    today = datetime.now().date()
    begin = time(8, 0)
    end = time(16, 30)
    pause = timedelta(minutes=30)
    tracker.track(today, begin, end, pause)

    begin = time(7, 30)
    tracker.track(today, begin, None, None)

    result = database.load(today)
    assert result
    assert result.begin == begin
    assert result.end == end
    assert result.pause == pause


def test_update_end_time():
    database, tracker = setup()
    today = datetime.now().date()
    begin = time(8, 0)
    end = time(16, 30)
    pause = timedelta(minutes=30)
    tracker.track(today, begin, end, pause)

    end = time(18, 0)
    tracker.track(today, None, end, None)

    result = database.load(today)
    assert result
    assert result.begin == begin
    assert result.end == end
    assert result.pause == pause


def test_update_pause_time():
    database, tracker = setup()
    today = datetime.now().date()
    begin = time(8, 0)
    end = time(16, 30)
    pause = timedelta(minutes=30)
    tracker.track(today, begin, end, pause)

    pause = timedelta(minutes=60)
    tracker.track(today, None, None, pause)

    result = database.load(today)
    assert result
    assert result.begin == begin
    assert result.end == end
    assert result.pause == pause


def test_raises_exception_on_stop_if_no_record_exist():
    database, tracker = setup()
    today = datetime.now().date()
    workday = database.load(today)
    if workday is not None:
        assert database.remove(today)

    with pytest.raises(RuntimeError):
        tracker.stop()


def test_raises_exception_if_start_is_none():
    database, tracker = setup()
    today = datetime.now().date()
    workday = database.load(today)
    if workday is not None:
        assert database.remove(today)

    with pytest.raises(ValueError):
        tracker.track(today, None, None, None)


# 8:30 -> 8:30
# 8:40 -> 8:30
# 8:41 -> 8:45
# 8:45 -> 8:45
@pytest.mark.parametrize("value,expected", [(time(8, 30), time(8, 30)), (time(8, 40, 59), time(8, 30)),
                                            (time(8, 41), time(8, 45)), (time(8, 44, 59), time(8, 45)),
                                            (time(19, 56), time(20, 00))])
def test_round_prev_quarter(value: time, expected: time):
    result = round_prev_quarter(value)

    assert result == expected


# 8:30 -> 8:30
# 8:35 -> 8:30
# 8:36 -> 8:45
# 8:45 -> 8:45
@pytest.mark.parametrize("value,expected", [(time(8, 30), time(8, 30)), (time(8, 35, 59), time(8, 30)),
                                            (time(8, 36), time(8, 45)), (time(8, 44, 59), time(8, 45)),
                                            (time(23, 56, 48), time(0, 0))])
def test_round_next_quarter(value: time, expected: time):
    result = round_next_quarter(value)

    assert result == expected
