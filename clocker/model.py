"""This module contains all models used in clocker"""

from dataclasses import dataclass
from datetime import date, datetime, time, timedelta


@dataclass
class WorkDay:
    """Model for storing all relevant information about a workday."""

    date: date
    start: time
    end: time
    pause: timedelta

    @property
    def duration(self) -> timedelta:
        """The duration is total hours worked at this day.

        Returns:
            timedelta: duration = end - start - pause
        """

        delta = (datetime.combine(self.date, self.end) - datetime.combine(self.date, self.start))
        return delta if self.pause >= delta else delta - self.pause
