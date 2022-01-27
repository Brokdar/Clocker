from datetime import date, time, timedelta

from clocker.model import WorkDay

from tests import db


def test_store_and_load_workday():
    database = db.get()
    day = date(2022, 1, 10)
    workday = WorkDay(day, time(8, 0), time(16, 30), timedelta(minutes=30))

    database.store(workday)

    result = database.load(day)
    assert workday == result


def test_modify_stored_workday():
    database = db.get()
    day = date(2022, 1, 10)
    workday = WorkDay(day, time(8, 0), time(16, 30), timedelta(minutes=30))
    database.store(workday)

    result = database.load(day)
    assert workday == result

    workday.pause = timedelta(minutes=60)
    database.store(workday)

    result = database.load(day)
    assert workday == result


def test_remove_workday():
    database = db.get()
    day = date(2022, 1, 10)
    workday = WorkDay(day, time(8, 0), time(16, 30), timedelta(minutes=30))
    database.store(workday)

    result = database.load(day)
    assert result == workday

    assert database.remove(day)
    result = database.load(day)
    assert result is None


def test_load_month():
    database = db.get()
    database.store(WorkDay(date(2022, 1, 10), time(8, 0), time(16, 30), timedelta(minutes=30)))
    database.store(WorkDay(date(2022, 1, 11), time(8, 0), time(17, 30), timedelta(minutes=60)))
    database.store(WorkDay(date(2022, 1, 12), time(8, 0), time(17, 30), timedelta(minutes=30)))
    database.store(WorkDay(date(2022, 1, 13), time(8, 0), time(17, 00), timedelta(minutes=45)))
    database.store(WorkDay(date(2022, 1, 14), time(8, 0), time(15, 30), timedelta(minutes=30)))

    result = database.load_month(1, 2022)
    assert result
    assert len(result) == 5
