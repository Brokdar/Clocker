from datetime import date, time, timedelta
from typing import Any

import pytest
from clocker import converter


def test_date_to_str():
    value = date(2022, 2, 1)

    result = converter.date_to_str(value)

    assert result == 'Tue 01.02.2022'


def test_time_to_str():
    value = time(hour=8, minute=00, second=30)

    result = converter.time_to_str(value)

    assert result == '08:00:30'


@pytest.mark.parametrize("value,expected", [(timedelta(hours=8, minutes=30), '8:30:00'),
                                            (timedelta(hours=-3, minutes=0), '-3:00:00'),
                                            (timedelta(hours=120, minutes=30), '120:30:00')])
def test_delta_to_str(value: timedelta, expected: str):
    result = converter.delta_to_str(value)

    assert result == expected


@pytest.mark.parametrize("value,expected", [('01.01.2022', date(2022, 1, 1)), ('11.10.2022', date(2022, 10, 11)),
                                            ('31.08.2022', date(2022, 8, 31))])
def test_str_to_date(value: str, expected: date):
    result = converter.str_to_date(value)

    assert result == expected


@pytest.mark.parametrize("value,expected", [('08:00:30', time(8, 0, 30)), ('12:30:45', time(12, 30, 45)),
                                            ('23:01:27', time(23, 1, 27)), ('15:50', time(15, 50)), ('7:30', time(7, 30))])
def test_str_to_time(value: str, expected: time):
    result = converter.str_to_time(value)

    assert result == expected


@pytest.mark.parametrize("value,expected", [('8:00', timedelta(hours=8)), ('16:20', timedelta(hours=16, minutes=20)),
                                            ('7:30:21', timedelta(hours=7, minutes=30, seconds=21))])
def test_str_to_delta(value: str, expected: timedelta):
    result = converter.str_to_delta(value)

    assert result == expected


@pytest.mark.parametrize("value,expected", [('true', True), ('false', False),
                                            ('8:35:57', timedelta(hours=8, minutes=35, seconds=57)),
                                            ('just a string', 'just a string')])
def test_str_to_value(value: str, expected: Any):
    result = converter.str_to_value(value)

    assert result == expected
