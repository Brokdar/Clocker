from datetime import date, time, timedelta

from clocker.model import WorkDay

from tests import db


def test_create_database_if_not_exists():
    database = db.get()
    day = date(2022, 1, 10)
    workday = WorkDay(date=day, begin=time(8, 0), end=time(16, 30), pause=timedelta(minutes=30))

    database.store(workday)
    assert db.exists()


def test_store_and_load_workday():
    database = db.get()
    day = date(2022, 1, 10)
    workday = WorkDay(date=day, begin=time(8, 0), end=time(16, 30), pause=timedelta(minutes=30))

    database.store(workday)

    result = database.load(day)
    assert workday == result


def test_modify_stored_workday():
    database = db.get()
    day = date(2022, 1, 10)
    workday = WorkDay(date=day, begin=time(8, 0), end=time(16, 30), pause=timedelta(minutes=30))
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
    workday = WorkDay(date=day, begin=time(8, 0), end=time(16, 30), pause=timedelta(minutes=30))
    database.store(workday)

    result = database.load(day)
    assert result == workday

    assert database.remove(day)
    result = database.load(day)
    assert result is None


def test_load_month():
    database = db.get()
    database.store(WorkDay(date=date(2022, 1, 10), begin=time(8, 0), end=time(16, 30), pause=timedelta(minutes=30)))
    database.store(WorkDay(date=date(2022, 1, 11), begin=time(8, 0), end=time(17, 30), pause=timedelta(minutes=60)))
    database.store(WorkDay(date=date(2022, 1, 12), begin=time(8, 0), end=time(17, 30), pause=timedelta(minutes=30)))
    database.store(WorkDay(date=date(2022, 1, 13), begin=time(8, 0), end=time(17, 00), pause=timedelta(minutes=45)))
    database.store(WorkDay(date=date(2022, 1, 14), begin=time(8, 0), end=time(15, 30), pause=timedelta(minutes=30)))

    result = database.load_month(1, 2022)
    assert result
    assert len(result) == 5
