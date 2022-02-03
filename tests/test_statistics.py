from datetime import date, time, timedelta

import pytest
from clocker.model import AbsenceType, WorkDay
from clocker.settings import Settings
from clocker.statistics import StatisticHandler, _count_workdays


@pytest.mark.parametrize("start,end,expected", [(date(2022, 1, 1), date(2022, 1, 31), 21),
                                                (date(2022, 1, 1), date(2022, 2, 4), 25),
                                                (date(2022, 1, 1), date(2022, 2, 28), 41),
                                                (date(2022, 1, 1), date(2022, 6, 30), 129),
                                                (date(2022, 1, 1), date(2022, 12, 31), 260)])
def test_count_target_working_days(start: date, end: date, expected: int):
    result = _count_workdays(start, end)

    assert result == expected


def test_collect_statistics_of_month():
    data = [
        WorkDay(date(2022, 1, 3), begin=time(8, 0), end=time(17, 0), pause=timedelta(hours=1)),
        WorkDay(date(2022, 1, 4), begin=time(8, 0), end=time(17, 0), pause=timedelta(hours=1)),
        WorkDay(date(2022, 1, 5), begin=time(8, 0), end=time(17, 0), pause=timedelta(hours=1)),
        WorkDay(date(2022, 1, 6), begin=time(8, 0), end=time(17, 0), pause=timedelta(hours=1)),
        WorkDay(date(2022, 1, 7), begin=time(8, 0), end=time(17, 0), pause=timedelta(hours=1)),
        WorkDay(date(2022, 1, 10), begin=time(8, 0), end=time(17, 0), pause=timedelta(hours=1)),
        WorkDay(date(2022, 1, 11), begin=time(8, 0), end=time(17, 0), pause=timedelta(hours=1)),
        WorkDay(date(2022, 1, 12), begin=time(8, 0), end=time(17, 0), pause=timedelta(hours=1)),
        WorkDay(date(2022, 1, 13), begin=time(8, 0), end=time(17, 0), pause=timedelta(hours=1)),
        WorkDay(date(2022, 1, 14), begin=time(8, 0), end=time(17, 0), pause=timedelta(hours=1)),
        WorkDay(date(2022, 1, 17), begin=time(8, 0), end=time(17, 0), pause=timedelta(hours=1)),
        WorkDay(date(2022, 1, 18), begin=time(8, 0), end=time(17, 0), pause=timedelta(hours=1)),
        WorkDay(date(2022, 1, 19), begin=time(8, 0), end=time(17, 0), pause=timedelta(hours=1)),
        WorkDay(date(2022, 1, 20), begin=time(8, 0), end=time(17, 0), pause=timedelta(hours=1)),
        WorkDay(date(2022, 1, 21), begin=time(8, 0), end=time(17, 0), pause=timedelta(hours=1)),
        WorkDay(date(2022, 1, 24), begin=time(8, 0), end=time(17, 0), pause=timedelta(hours=1)),
        WorkDay(date(2022, 1, 25), begin=time(8, 0), end=time(17, 0), pause=timedelta(hours=1)),
        WorkDay(date(2022, 1, 26), begin=time(8, 0), end=time(17, 0), pause=timedelta(hours=1)),
        WorkDay(date(2022, 1, 27), begin=time(8, 0), end=time(17, 0), pause=timedelta(hours=1)),
        WorkDay(date(2022, 1, 28), begin=time(8, 0), end=time(17, 0), pause=timedelta(hours=1)),
        WorkDay(date(2022, 1, 31), begin=time(8, 0), end=time(17, 0), pause=timedelta(hours=1)),
    ]

    handler = StatisticHandler(Settings('tests/settings.ini'))
    result = handler.collect(data)

    assert result
    assert result.target_working_days == 21
    assert result.target_working_hours == timedelta(hours=168)
    assert result.count.work == 21
    assert result.count.vacation == 0
    assert result.count.flex == 0
    assert result.count.sick == 0
    assert result.working_hours == timedelta(hours=168)
    assert result.flextime == timedelta(0)


def test_including_vacation():
    data = [
        WorkDay(date(2022, 1, 3), absence=AbsenceType.VACATION),
        WorkDay(date(2022, 1, 4), absence=AbsenceType.VACATION),
        WorkDay(date(2022, 1, 5), absence=AbsenceType.VACATION),
        WorkDay(date(2022, 1, 6), absence=AbsenceType.VACATION),
        WorkDay(date(2022, 1, 7), absence=AbsenceType.VACATION),
        WorkDay(date(2022, 1, 10), begin=time(8, 0), end=time(17, 0), pause=timedelta(hours=1)),
        WorkDay(date(2022, 1, 11), begin=time(8, 0), end=time(17, 0), pause=timedelta(hours=1)),
        WorkDay(date(2022, 1, 12), begin=time(8, 0), end=time(17, 0), pause=timedelta(hours=1)),
        WorkDay(date(2022, 1, 13), begin=time(8, 0), end=time(17, 0), pause=timedelta(hours=1)),
        WorkDay(date(2022, 1, 14), begin=time(8, 0), end=time(17, 0), pause=timedelta(hours=1)),
        WorkDay(date(2022, 1, 17), begin=time(8, 0), end=time(17, 0), pause=timedelta(hours=1)),
        WorkDay(date(2022, 1, 18), begin=time(8, 0), end=time(17, 0), pause=timedelta(hours=1)),
        WorkDay(date(2022, 1, 19), begin=time(8, 0), end=time(17, 0), pause=timedelta(hours=1)),
        WorkDay(date(2022, 1, 20), begin=time(8, 0), end=time(17, 0), pause=timedelta(hours=1)),
        WorkDay(date(2022, 1, 21), begin=time(8, 0), end=time(17, 0), pause=timedelta(hours=1)),
        WorkDay(date(2022, 1, 24), begin=time(8, 0), end=time(17, 0), pause=timedelta(hours=1)),
        WorkDay(date(2022, 1, 25), begin=time(8, 0), end=time(17, 0), pause=timedelta(hours=1)),
        WorkDay(date(2022, 1, 26), begin=time(8, 0), end=time(17, 0), pause=timedelta(hours=1)),
        WorkDay(date(2022, 1, 27), begin=time(8, 0), end=time(17, 0), pause=timedelta(hours=1)),
        WorkDay(date(2022, 1, 28), begin=time(8, 0), end=time(17, 0), pause=timedelta(hours=1)),
        WorkDay(date(2022, 1, 31), begin=time(8, 0), end=time(17, 0), pause=timedelta(hours=1))
    ]

    handler = StatisticHandler(Settings('tests/settings.ini'))
    result = handler.collect(data)

    assert result
    assert result.target_working_days == 21
    assert result.target_working_hours == timedelta(hours=168)
    assert result.count.work == 16
    assert result.count.vacation == 5
    assert result.count.flex == 0
    assert result.count.sick == 0
    assert result.working_hours == timedelta(hours=168)
    assert result.flextime == timedelta(0)


def test_including_sickness():
    data = [
        WorkDay(date(2022, 1, 3), absence=AbsenceType.SICKNESS),
        WorkDay(date(2022, 1, 4), absence=AbsenceType.SICKNESS),
        WorkDay(date(2022, 1, 5), absence=AbsenceType.SICKNESS),
        WorkDay(date(2022, 1, 6), absence=AbsenceType.SICKNESS),
        WorkDay(date(2022, 1, 7), absence=AbsenceType.SICKNESS),
        WorkDay(date(2022, 1, 10), begin=time(8, 0), end=time(17, 0), pause=timedelta(hours=1)),
        WorkDay(date(2022, 1, 11), begin=time(8, 0), end=time(17, 0), pause=timedelta(hours=1)),
        WorkDay(date(2022, 1, 12), begin=time(8, 0), end=time(17, 0), pause=timedelta(hours=1)),
        WorkDay(date(2022, 1, 13), begin=time(8, 0), end=time(17, 0), pause=timedelta(hours=1)),
        WorkDay(date(2022, 1, 14), begin=time(8, 0), end=time(17, 0), pause=timedelta(hours=1)),
        WorkDay(date(2022, 1, 17), begin=time(8, 0), end=time(17, 0), pause=timedelta(hours=1)),
        WorkDay(date(2022, 1, 18), begin=time(8, 0), end=time(17, 0), pause=timedelta(hours=1)),
        WorkDay(date(2022, 1, 19), begin=time(8, 0), end=time(17, 0), pause=timedelta(hours=1)),
        WorkDay(date(2022, 1, 20), begin=time(8, 0), end=time(17, 0), pause=timedelta(hours=1)),
        WorkDay(date(2022, 1, 21), begin=time(8, 0), end=time(17, 0), pause=timedelta(hours=1)),
        WorkDay(date(2022, 1, 24), begin=time(8, 0), end=time(17, 0), pause=timedelta(hours=1)),
        WorkDay(date(2022, 1, 25), begin=time(8, 0), end=time(17, 0), pause=timedelta(hours=1)),
        WorkDay(date(2022, 1, 26), begin=time(8, 0), end=time(17, 0), pause=timedelta(hours=1)),
        WorkDay(date(2022, 1, 27), begin=time(8, 0), end=time(17, 0), pause=timedelta(hours=1)),
        WorkDay(date(2022, 1, 28), begin=time(8, 0), end=time(17, 0), pause=timedelta(hours=1)),
        WorkDay(date(2022, 1, 31), begin=time(8, 0), end=time(17, 0), pause=timedelta(hours=1))
    ]

    handler = StatisticHandler(Settings('tests/settings.ini'))
    result = handler.collect(data)

    assert result
    assert result.target_working_days == 21
    assert result.target_working_hours == timedelta(hours=168)
    assert result.count.work == 16
    assert result.count.vacation == 0
    assert result.count.flex == 0
    assert result.count.sick == 5
    assert result.working_hours == timedelta(hours=168)
    assert result.flextime == timedelta(0)


def test_including_flexdays():
    data = [
        WorkDay(date(2022, 1, 3), absence=AbsenceType.FLEXDAY),
        WorkDay(date(2022, 1, 4), absence=AbsenceType.FLEXDAY),
        WorkDay(date(2022, 1, 5), absence=AbsenceType.FLEXDAY),
        WorkDay(date(2022, 1, 6), absence=AbsenceType.FLEXDAY),
        WorkDay(date(2022, 1, 7), absence=AbsenceType.FLEXDAY),
        WorkDay(date(2022, 1, 10), begin=time(8, 0), end=time(17, 0), pause=timedelta(hours=1)),
        WorkDay(date(2022, 1, 11), begin=time(8, 0), end=time(17, 0), pause=timedelta(hours=1)),
        WorkDay(date(2022, 1, 12), begin=time(8, 0), end=time(17, 0), pause=timedelta(hours=1)),
        WorkDay(date(2022, 1, 13), begin=time(8, 0), end=time(17, 0), pause=timedelta(hours=1)),
        WorkDay(date(2022, 1, 14), begin=time(8, 0), end=time(17, 0), pause=timedelta(hours=1)),
        WorkDay(date(2022, 1, 17), begin=time(8, 0), end=time(17, 0), pause=timedelta(hours=1)),
        WorkDay(date(2022, 1, 18), begin=time(8, 0), end=time(17, 0), pause=timedelta(hours=1)),
        WorkDay(date(2022, 1, 19), begin=time(8, 0), end=time(17, 0), pause=timedelta(hours=1)),
        WorkDay(date(2022, 1, 20), begin=time(8, 0), end=time(17, 0), pause=timedelta(hours=1)),
        WorkDay(date(2022, 1, 21), begin=time(8, 0), end=time(17, 0), pause=timedelta(hours=1)),
        WorkDay(date(2022, 1, 24), begin=time(8, 0), end=time(17, 0), pause=timedelta(hours=1)),
        WorkDay(date(2022, 1, 25), begin=time(8, 0), end=time(17, 0), pause=timedelta(hours=1)),
        WorkDay(date(2022, 1, 26), begin=time(8, 0), end=time(17, 0), pause=timedelta(hours=1)),
        WorkDay(date(2022, 1, 27), begin=time(8, 0), end=time(17, 0), pause=timedelta(hours=1)),
        WorkDay(date(2022, 1, 28), begin=time(8, 0), end=time(17, 0), pause=timedelta(hours=1)),
        WorkDay(date(2022, 1, 31), begin=time(8, 0), end=time(17, 0), pause=timedelta(hours=1))
    ]

    handler = StatisticHandler(Settings('tests/settings.ini'))
    result = handler.collect(data)

    assert result
    assert result.target_working_days == 21
    assert result.target_working_hours == timedelta(hours=168)
    assert result.count.work == 16
    assert result.count.vacation == 0
    assert result.count.flex == 5
    assert result.count.sick == 0
    assert result.working_hours == timedelta(hours=128)
    assert result.flextime == timedelta(hours=-40)


def test_flexdays_over_month_borders():
    data = [
        WorkDay(date(2022, 1, 3), begin=time(8, 0), end=time(17, 30), pause=timedelta(hours=1)),
        WorkDay(date(2022, 1, 4), begin=time(8, 0), end=time(17, 30), pause=timedelta(hours=1)),
        WorkDay(date(2022, 1, 5), begin=time(8, 0), end=time(17, 30), pause=timedelta(hours=1)),
        WorkDay(date(2022, 1, 6), begin=time(8, 0), end=time(17, 30), pause=timedelta(hours=1)),
        WorkDay(date(2022, 1, 7), begin=time(8, 0), end=time(17, 30), pause=timedelta(hours=1)),
        WorkDay(date(2022, 1, 10), begin=time(8, 0), end=time(17, 0), pause=timedelta(hours=1)),
        WorkDay(date(2022, 1, 11), begin=time(8, 0), end=time(17, 0), pause=timedelta(hours=1)),
        WorkDay(date(2022, 1, 12), begin=time(8, 0), end=time(17, 0), pause=timedelta(hours=1)),
        WorkDay(date(2022, 1, 13), begin=time(8, 0), end=time(17, 0), pause=timedelta(hours=1)),
        WorkDay(date(2022, 1, 14), begin=time(8, 0), end=time(17, 0), pause=timedelta(hours=1)),
        WorkDay(date(2022, 1, 17), begin=time(8, 0), end=time(17, 0), pause=timedelta(hours=1)),
        WorkDay(date(2022, 1, 18), begin=time(8, 0), end=time(17, 0), pause=timedelta(hours=1)),
        WorkDay(date(2022, 1, 19), begin=time(8, 0), end=time(17, 0), pause=timedelta(hours=1)),
        WorkDay(date(2022, 1, 20), begin=time(8, 0), end=time(17, 0), pause=timedelta(hours=1)),
        WorkDay(date(2022, 1, 21), begin=time(8, 0), end=time(17, 0), pause=timedelta(hours=1)),
        WorkDay(date(2022, 1, 24), begin=time(8, 0), end=time(17, 0), pause=timedelta(hours=1)),
        WorkDay(date(2022, 1, 25), begin=time(8, 0), end=time(17, 0), pause=timedelta(hours=1)),
        WorkDay(date(2022, 1, 26), begin=time(8, 0), end=time(17, 0), pause=timedelta(hours=1)),
        WorkDay(date(2022, 1, 27), begin=time(8, 0), end=time(17, 0), pause=timedelta(hours=1)),
        WorkDay(date(2022, 1, 28), begin=time(8, 0), end=time(17, 0), pause=timedelta(hours=1)),
        WorkDay(date(2022, 1, 31), begin=time(8, 0), end=time(17, 30), pause=timedelta(hours=1)),
        WorkDay(date(2022, 2, 1), begin=time(8, 0), end=time(17, 30), pause=timedelta(hours=1)),
        WorkDay(date(2022, 2, 2), begin=time(8, 0), end=time(17, 30), pause=timedelta(hours=1)),
        WorkDay(date(2022, 2, 3), begin=time(8, 0), end=time(17, 30), pause=timedelta(hours=1)),
        WorkDay(date(2022, 2, 4), begin=time(8, 0), end=time(17, 30), pause=timedelta(hours=1))
    ]

    handler = StatisticHandler(Settings('tests/settings.ini'))
    result = handler.collect(data)

    assert result
    assert result.target_working_days == 25
    assert result.target_working_hours == timedelta(hours=200)
    assert result.count.work == 25
    assert result.count.vacation == 0
    assert result.count.flex == 0
    assert result.count.sick == 0
    assert result.working_hours == timedelta(hours=205)
    assert result.flextime == timedelta(hours=5)


def test_missing_records_at_beginning_of_month():
    data = [
        WorkDay(date(2022, 1, 10), begin=time(8, 0), end=time(17, 0), pause=timedelta(hours=1)),
        WorkDay(date(2022, 1, 11), begin=time(8, 0), end=time(17, 0), pause=timedelta(hours=1)),
        WorkDay(date(2022, 1, 12), begin=time(8, 0), end=time(17, 0), pause=timedelta(hours=1)),
        WorkDay(date(2022, 1, 13), begin=time(8, 0), end=time(17, 0), pause=timedelta(hours=1)),
        WorkDay(date(2022, 1, 14), begin=time(8, 0), end=time(17, 0), pause=timedelta(hours=1)),
        WorkDay(date(2022, 1, 17), begin=time(8, 0), end=time(17, 0), pause=timedelta(hours=1)),
        WorkDay(date(2022, 1, 18), begin=time(8, 0), end=time(17, 0), pause=timedelta(hours=1)),
        WorkDay(date(2022, 1, 19), begin=time(8, 0), end=time(17, 0), pause=timedelta(hours=1)),
        WorkDay(date(2022, 1, 20), begin=time(8, 0), end=time(17, 0), pause=timedelta(hours=1)),
        WorkDay(date(2022, 1, 21), begin=time(8, 0), end=time(17, 0), pause=timedelta(hours=1))
    ]

    handler = StatisticHandler(Settings('tests/settings.ini'))
    result = handler.collect(data)

    assert result
    assert result.target_working_days == 15
    assert result.target_working_hours == timedelta(hours=120)
    assert result.count.work == 10
    assert result.count.vacation == 0
    assert result.count.flex == 0
    assert result.count.sick == 0
    assert result.working_hours == timedelta(hours=80)
    assert result.flextime == timedelta(hours=-40)
