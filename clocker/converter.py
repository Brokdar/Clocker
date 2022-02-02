"""Utility conversion functions for handling date and time"""

from datetime import date, datetime, time, timedelta
from typing import Any

from clocker.model import AbsenceType


def date_to_str(value: date) -> str:
    """Returns the string representation of a given date.

    Args:
        date (date): date to be displayed

    Returns:
        str: %a %d.%m.%Y
    """

    return value.strftime("%a %d.%m.%Y")


def time_to_str(value: time) -> str:
    """Returns the string representation of a given time.

    Args:
        time (time): time to be displayed

    Returns:
        str: %H:%M:%S
    """

    return value.strftime("%H:%M:%S")


def delta_to_str(value: timedelta) -> str:
    """Returns the string representation of a given timedelta.

    Args:
        value (timedelta): timedelta to be displayed

    Returns:
        str: negative or positive timedelta
    """

    def convert(value: timedelta) -> str:
        total_seconds = int(value.total_seconds())
        seconds = total_seconds % 60
        minutes = (total_seconds // 60) % 60
        hours = (total_seconds // 3600)

        return f'{hours}:{minutes:02}:{seconds:02}'

    if value < timedelta(0):
        return '-' + convert(-value)
    return convert(value)


def str_to_date(value: str) -> date:
    """Parses a string value to a date representation.

    Args:
        value (str): string in the format of '%d.%m.%y'

    Returns:
        date: date representation
    """

    return datetime.strptime(value, '%d.%m.%Y').date()


def str_to_time(value: str) -> time:
    """Parses a string value to a time representation.

    Args:
        value (str): string in the format of '%H:%M'

    Returns:
        time: time representation
    """

    if value.count(':') > 1:
        return datetime.strptime(value, '%H:%M:%S').time()
    return datetime.strptime(value, '%H:%M').time()


def str_to_delta(value: str) -> timedelta:
    """Parses a string value to a time delta representation.

    Args:
        value (str): string in the format of '%H:%M'

    Returns:
        timedelta: time delta representation
    """

    _time = str_to_time(value)
    return timedelta(hours=_time.hour, minutes=_time.minute, seconds=_time.second)


def str_to_value(value: str) -> Any:
    """Converts a string to any value.
    Supported types:
    - bool
    - timedelta
    - str

    Args:
        value (str): Value to convert.

    Returns:
        Any: type of value, str if no conversion found.
    """

    if value is None:
        return None

    try:
        if value in ['true', 'false']:
            return value == 'true'

        if ':' in value:
            return str_to_delta(value)

        if value.isdigit():
            return int(value)

        return value

    except ValueError:
        return value


def enum_to_abbreviation(value: AbsenceType) -> str:
    """Converts an AbsenceType to an abbreviation string.

    Args:
        value (AbsenceType): Absence type

    Raises:
        Exception: Conversion exception

    Returns:
        str: Abbreviation of the absence type
    """

    match value:
        case AbsenceType.WORKDAY:
            return 'W'
        case AbsenceType.VACATION:
            return 'V'
        case AbsenceType.FLEXDAY:
            return 'F'
        case AbsenceType.SICKNESS:
            return 'S'
        case AbsenceType.HOLIDAY:
            return 'H'
        case _:
            raise ValueError(f'Invalid AbsenceType cannot be converted to abbreviation: {value}')
