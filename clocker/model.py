"""This module contains all models used in clocker"""

from __future__ import annotations

from datetime import date, datetime, time, timedelta
from enum import Enum
from typing import Optional

from pydantic import BaseModel


class AbsenceType(Enum):
    """Enumeration for each type of absence"""

    WORKDAY = 0
    VACATION = 1
    FLEXDAY = 2
    SICKNESS = 3
    HOLIDAY = 4

    @staticmethod
    def from_abbreviation(abbr: str) -> AbsenceType:
        """Converts abbreviation to AbsenceType

        Args:
            abbr (str): Abbreviation string [W,F,V,S,H]

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
            case 'H':
                return AbsenceType.HOLIDAY
            case _:
                raise ValueError(f'invalid abbreviation string: {abbr}')


class WorkDay(BaseModel):
    """Model for storing all relevant information about a workday."""

    date: date
    absence: AbsenceType = AbsenceType.WORKDAY
    begin: Optional[time] = None
    end: Optional[time] = None
    pause: timedelta = timedelta(0)

    class Config:
        validate_assignment: True

    def __str__(self) -> str:
        if self.absence != AbsenceType.WORKDAY:
            return f'Workday(date={self.date}, absence={self.absence})'

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

        return self.dict(exclude={'date'})

    @classmethod
    def decode(cls, data: dict) -> WorkDay:
        """Decodes a dictionary loaded from json file into a WorkDay object.

        Args:
            data (dict): Dictionary representation of a WorkDay model

        Returns:
            WorkDay: WorkDay instance
        """

        data['date'] = data.doc_id
        return WorkDay.parse_obj(data)
