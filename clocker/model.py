"""This module contains all models used in clocker"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from typing import Optional


@dataclass
class WorkDayStatistics:
    """Model for storing statistics about a set of WorkDays"""
    avg_start: time = time()
    avg_end: time = time()
    avg_pause: timedelta = timedelta(0)
    sum_duration: timedelta = timedelta(0)
    sum_flextime: timedelta = timedelta(0)

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

    @classmethod
    def decode(cls, data: dict) -> WorkDay:
        """Decodes a dictionary loaded from json file into a WorkDay object.

        Args:
            data (dict): Dictionary representation of a WorkDay model

        Returns:
            WorkDay: WorkDay instance
        """

        if not all(key in data for key in ['date', 'start', 'end', 'pause']):
            raise KeyError(f'Not all keys are available for {data}')

        day = date.fromisoformat(data['date'])
        start = time.fromisoformat(data['start']) if data['start'] is not None else None
        end = time.fromisoformat(data['end']) if data['end'] is not None else None
        t_pause = time.fromisoformat(data['pause']) if data['pause'] is not None else None
        pause = timedelta(
            hours=t_pause.hour, minutes=t_pause.minute, seconds=t_pause.second
        ) if t_pause is not None else timedelta(0)

        return cls(day, start, end, pause)

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
