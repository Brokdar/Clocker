from datetime import datetime, time, timedelta

from clocker import database, tracker


def test_start_tracking():
    today = datetime.now().date()
    result = database.load(today)

    if result is not None:
        database.remove(today)

    tracker.start()

    result = database.load(today)
    assert result
    assert result.date == today
    assert result.start is not None
    assert result.end is None
    assert result.pause is not None

def test_stop_tracking():
    today = datetime.now().date()

    tracker.start()
    result = database.load(today)
    assert result

    tracker.stop()

    result = database.load(today)
    assert result
    assert result.date == today
    assert result.start is not None
    assert result.end is not None
    assert result.pause is not None

def test_track_manually():
    today = datetime.now().date()
    begin = time(8,0)
    end = time(16,30)
    pause = timedelta(minutes=30)
    tracker.track(today, begin, end, pause)

    result = database.load(today)
    assert result
    assert result.date == today
    assert result.start == begin
    assert result.end == end
    assert result.pause == pause

def test_update_start_time():
    today = datetime.now().date()
    begin = time(8,0)
    end = time(16,30)
    pause = timedelta(minutes=30)
    tracker.track(today, begin, end, pause)

    begin = time(7,30)
    tracker.track(today, begin, end, pause)

    result = database.load(today)
    assert result
    assert result.start == begin

def test_update_end_time():
    today = datetime.now().date()
    begin = time(8,0)
    end = time(16,30)
    pause = timedelta(minutes=30)
    tracker.track(today, begin, end, pause)

    end = time(18,0)
    tracker.track(today, begin, end, pause)

    result = database.load(today)
    assert result
    assert result.end == end

def test_update_pause_time():
    today = datetime.now().date()
    begin = time(8,0)
    end = time(16,30)
    pause = timedelta(minutes=30)
    tracker.track(today, begin, end, pause)

    pause = timedelta(minutes=60)
    tracker.track(today, begin, end, pause)

    result = database.load(today)
    assert result
    assert result.pause == pause