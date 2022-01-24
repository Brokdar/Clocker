"""This module tracks the working hours"""

from datetime import date, datetime, time, timedelta
from typing import Optional

from clocker.database import Database
from clocker.model import Statistics, WorkDay
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
        if workday:
            return workday

        if self.__settings.read('Behavior', 'RoundToQuarter'):
            begin = round_prev_quarter(now.time())
        else:
            begin = now.replace(microsecond=0).time()

        workday = WorkDay(
            date=now.date(),
            begin=begin
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

        if workday.end and now.time() < workday.end:
            return workday

        if self.__settings.read('Behavior', 'RoundToQuarter'):
            end = round_next_quarter(now.time())
        else:
            end = now.replace(microsecond=0).time()

        workday.end = end
        if workday.duration > timedelta(hours=6):
            pause = self.__settings.read('Workday', 'PauseTime')
            if pause:
                workday.pause = pause

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
            workday.begin = begin or workday.begin
            workday.end = end or workday.end
            workday.pause = pause or workday.pause

        if workday.begin is None:
            raise ValueError('[Error] start time of workday cannot be None')

        self.__db.store(workday)
        return workday


class TimeManager:
    """Class for managing the work time data"""

    def __init__(self, settings: Settings):
        self.__settings = settings

    def statistics(self, data: list[WorkDay]) -> Statistics:
        """Evaluates statistics of a given list of WorkDay objects

        Args:
            data (list[WorkDay]): list of WorkDay objects

        Returns:
            WorkDayStatistics: Statistical information about the list of WorkDay
        """

        def add(_delta: timedelta, _time: time) -> timedelta:
            return _delta + timedelta(hours=_time.hour, minutes=_time.minute, seconds=_time.second)

        statistics = Statistics()
        if not data:
            return statistics

        avg_start = timedelta(0)
        avg_end = timedelta(0)

        for day in data:
            avg_start = add(avg_start, day.begin)
            avg_end = add(avg_end, day.end)
            statistics.avg_pause += day.pause
            statistics.sum_duration += day.duration
            statistics.sum_flextime += self.flextime(day)

        avg_start = avg_start / len(data)
        avg_end = avg_end / len(data)
        statistics.avg_pause /= len(data)

        statistics.avg_begin = (datetime.min + avg_start).time()
        statistics.avg_end = (datetime.min + avg_end).time()

        return statistics

    def flextime(self, data: WorkDay) -> timedelta:
        """Calculates the flextime for the given day

        Args:
            data (WorkDay): day for which the flextime should be calculated

        Returns:
            timedelta: flextime
        """

        return data.duration - self.__settings.read('Workday', 'Duration')

def round_prev_quarter(value: time):
    """Rounds the time to the previous quarter.

    Args:
        value (time): Time that should be rounded

    Returns:
        [type]: Rounded time to the previous quarter
    """

    minutes = 15 * (value.minute // 15)
    return time(value.hour, minutes)

def round_next_quarter(value: time):
    """Rounds the time to the next quarter.

    Args:
        value (time): Time that should be rounded

    Returns:
        [type]: Rounded time to the next quarter
    """

    hours = value.hour
    minutes = 15 * ((value.minute + 15) // 15)

    if minutes == 60:
        minutes = 0
        hours = hours + 1 if hours != 23 else 0

    return time(hours, minutes)
