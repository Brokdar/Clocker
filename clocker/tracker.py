"""This module tracks the working hours"""

from datetime import date, datetime, time, timedelta
from typing import Optional

from clocker.database import Database
from clocker.model import WorkDay
from clocker.settings import Settings


class Tracker:
    """Class to track the work time."""

    def __init__(self, settings: Settings, database: Database):
        self.__settings = settings
        self.__db = database

    def start(self) -> WorkDay:
        """Starts tracking of working hours for the current day. Sets start time to current time.

        Returns:
            WorkDay: [description]
        """

        now = datetime.now()
        workday = self.__db.load(now.date())
        if workday is not None:
            return workday

        workday = WorkDay(
            date=now.date(),
            start=now.time(),
            pause=self.__settings.read('Workday', 'PauseTime')
        )

        self.__db.store(workday)
        return workday

    def stop(self) -> WorkDay:
        """Stops the tracking of working hours for the current day. Sets end time to current time.

        Raises:
            RuntimeError: raised if stop has been called before start

        Returns:
            WorkDay: workday model with the input values set
        """

        now = datetime.now()
        workday = self.__db.load(now.date())
        if workday is None:
            raise RuntimeError('[Error] start() must be called before stop()')

        workday.end = now.time()
        self.__db.store(workday)
        return workday

    def track(self, day: date, begin: Optional[time], end: Optional[time], pause: Optional[timedelta]) -> WorkDay:
        """Add a new weekday records to the database with the given values.

        Args:
            day (date): date of workday
            begin (Optional[time]): begin of work
            end (Optional[time]): end of work
            pause (Optional[timedelta]): pause duration

        Raises:
            ValueError: raised if invalid data has been passed

        Returns:
            WorkDay: workday model with the input values set
        """

        workday = self.__db.load(day)
        if workday is None:
            if pause is None:
                pause = self.__settings.read('Workday', 'PauseTime')
            workday = WorkDay(day, begin, end, pause)
        else:
            workday.start = begin or workday.start
            workday.end = end or workday.end
            workday.pause = pause or workday.pause

        if workday.start is None:
            raise ValueError('[Error] start time of workday cannot be None')

        self.__db.store(workday)
        return workday
