"""This module contains all models used in clocker"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from enum import Enum
from typing import Optional


class AbsenceType(Enum):
    """Enumeration for each type of absence"""

    WORKDAY = 0
    VACATION = 1
    FLEXDAY = 2
    SICKNESS = 3

    @staticmethod
    def from_abbreviation(abbr: str) -> AbsenceType:
        """Converts abbreviation to AbsenceType

        Args:
            abbr (str): Abbreviation string [W,F,V,S]

        Raises:
            ValueError: invalid abbreviation string

        Returns:
            AbsenceType: Absence type converted from abbreviation
        """

        match abbr.upper():
            case 'W':
                return AbsenceType.WORKDAY
            case 'V':
                return AbsenceType.VACATION
            case 'F':
                return AbsenceType.FLEXDAY
            case 'S':
                return AbsenceType.SICKNESS
            case _:
                raise ValueError(f'invalid abbreviation string: {abbr}')


@dataclass
class Statistics:
    """Model for storing statistics about a set of WorkDays"""

    avg_begin: time = time()
    avg_end: time = time()
    avg_pause: timedelta = timedelta(0)
    sum_duration: timedelta = timedelta(0)
    sum_flextime: timedelta = timedelta(0)


@dataclass
class WorkDay:
    """Model for storing all relevant information about a workday."""

    date: date
    absence: AbsenceType = AbsenceType.WORKDAY
    begin: Optional[time] = None
    end: Optional[time] = None
    pause: timedelta = timedelta(0)

    def __str__(self) -> str:
        if self.absence != AbsenceType.WORKDAY:
            return f'Workday(date={self.date}, absence={self.absence}'

        return f'Workday(date={self.date}, begin={self.begin}, end={self.end}, pause={self.pause})'

    @property
    def duration(self) -> timedelta:
        """The duration is total hours worked at this day.

        Returns:
            timedelta: duration = end - start - pause
        """

        if self.begin is not None and self.end is not None:
            delta = datetime.combine(self.date, self.end) - datetime.combine(self.date, self.begin)
            return delta if self.pause >= delta else delta - self.pause

        return timedelta(0)

    def is_absence_day(self) -> bool:
        """Returns true if its a absence day or a regular workday

        Returns:
            bool: True if absence day, False if regular workday
        """

        return self.absence != AbsenceType.WORKDAY

    def encode(self) -> dict:
        """Encodes a WorkDay object into a dictionary representation.

        Returns:
            dict: Dictionary instance
        """

        data = self.__dict__.copy()
        del data['date']

        return data

    @classmethod
    def decode(cls, data: dict) -> WorkDay:
        """Decodes a dictionary loaded from json file into a WorkDay object.

        Args:
            data (dict): Dictionary representation of a WorkDay model

        Returns:
            WorkDay: WorkDay instance
        """

        if not all(key in data for key in ['begin', 'end', 'pause']):
            raise KeyError(f'Not all keys are available for {data}')

        absence = AbsenceType(data['absence']) if data['absence'] is not None else AbsenceType.WORKDAY
        start = time.fromisoformat(data['begin']) if data['begin'] is not None else None
        end = time.fromisoformat(data['end']) if data['end'] is not None else None
        t_pause = time.fromisoformat(data['pause']) if data['pause'] is not None else None
        pause = timedelta(hours=t_pause.hour, minutes=t_pause.minute,
                          seconds=t_pause.second) if t_pause is not None else timedelta(0)

        return cls(data.doc_id, absence, start, end, pause)
