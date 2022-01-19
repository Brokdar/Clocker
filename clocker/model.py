"""This module contains all models used in clocker"""

from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from typing import Optional


@dataclass
class WorkDay:
    """Model for storing all relevant information about a workday."""

    date: date
    start: Optional[time] = None
    end: Optional[time] = None
    pause: timedelta = timedelta(0)

    @property
    def duration(self) -> timedelta:
        """The duration is total hours worked at this day.

        Returns:
            timedelta: duration = end - start - pause
        """

        if self.start is not None and self.end is not None:
            delta = (datetime.combine(self.date, self.end) - datetime.combine(self.date, self.start))
            return delta if self.pause >= delta else delta - self.pause

        return timedelta(0)

def parse_date(value: str) -> date:
    """Parses a string value to a date representation.

    Args:
        value (str): string in the format of '%d.%m.%y'

    Returns:
        date: date representation
    """

    return datetime.strptime(value, '%d.%m.%Y').date()

def parse_time(value: str) -> time:
    """Parses a string value to a time representation.

    Args:
        value (str): string in the format of '%H:%M'

    Returns:
        time: time representation
    """

    return datetime.strptime(value, '%H:%M').time()

def parse_delta(value: str) -> timedelta:
    """Parses a string value to a time delta representation.

    Args:
        value (str): string in the format of '%H:%M'

    Returns:
        timedelta: time delta representation
    """

    _time = parse_time(value)
    return timedelta(hours=_time.hour, minutes=_time.minute)
