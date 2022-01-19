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
    pause: Optional[timedelta] = timedelta(0)

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
