"""This module tracks the working hours"""

import logging
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
            logging.info('Start (%s) - already present in database', now.date())
            return workday

        if self.__settings.read('Behavior', 'RoundToQuarter'):
            begin = round_prev_quarter(now.time())
            logging.debug('Start (%s) - round to previous quarter (%s -> %s)', now.date(), now.time(), begin)
        else:
            begin = now.replace(microsecond=0).time()

        workday = WorkDay(date=now.date(), begin=begin)

        self.__db.store(workday)
        logging.info('Start (%s) - start tracking %s', workday.date, workday)

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

        if self.__settings.read('Behavior', 'RoundToQuarter'):
            end = round_next_quarter(now.time())
            logging.debug('Stop (%s) - round to next quarter (%s -> %s)', workday.date, now.time(), end)
        else:
            end = now.replace(microsecond=0).time()

        updated = False
        if workday.end:
            if end <= workday.end:
                logging.info('Stop (%s) - current time is before tracked time (%s <= %s)', workday.date, end, workday.end)
                return workday

            updated = True
            old_end = workday.end

        workday.end = end
        self.__set_pause(workday)
        self.__db.store(workday)

        if updated:
            logging.info('Stop (%s) - update end time (%s -> %s)', workday.date, old_end, end)
        else:
            logging.info('Stop (%s) - stop tracking %s', now.date(), workday)

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
            workday = WorkDay(day)
            logging.info('Track (%s) - create new workday', workday.date)
        else:
            logging.info('Track (%s) - update %s', workday.date, workday)

        workday.begin = begin or workday.begin
        workday.end = end or workday.end
        workday.pause = pause or workday.pause

        if workday.pause == timedelta(0):
            self.__set_pause(workday)

        if workday.begin is None:
            raise ValueError('[Error] start time of workday cannot be None')

        self.__db.store(workday)
        logging.info('Track (%s) - set %s', workday.date, workday)

        return workday

    def __set_pause(self, workday: WorkDay):
        if workday.pause > timedelta(0):
            return

        if workday.end is not None:
            if workday.duration > timedelta(hours=6):
                pause = self.__settings.read('Workday', 'PauseTime')
                if pause:
                    workday.pause = pause
                    logging.debug('Stop (%s) - set pause time from settings to %s', workday.date, pause)
                else:
                    logging.warning("Stop (%s) - no 'PauseTime' configured in settings", workday.date)
            else:
                logging.debug('Stop (%s) - no pause time set because duration is less than 6 hours', workday.date)
        else:
            logging.debug('Stop (%s) - no end time set therefore no pause time applied', workday.date)

    def remove(self, day: date):
        """Remove a WorkDay from the database

        Args:
            day (date): Date of WorkDay

        Raises:
            ValueError: Unexpected error while remove the WorkDay from the database
        """

        workday = self.__db.load(day)
        if workday is None:
            logging.info('Remove (%s) - no workday found', day)
            return

        if self.__db.remove(day):
            logging.info('Remove (%s) - removed %s', day, workday)
        else:
            raise ValueError(f'[Error] removing workday({day}) from database')


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
            if _time:
                return _delta + timedelta(hours=_time.hour, minutes=_time.minute, seconds=_time.second)
            return _delta

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


def round_prev_quarter(value: time) -> time:
    """Rounds the time to the previous quarter.

    Args:
        value (time): Time that should be rounded

    Returns:
        [type]: Rounded time to the previous quarter
    """

    quarter = 15
    remainder = value.minute % quarter
    if remainder > 10:
        minutes = _round(value.minute + quarter, quarter)
    else:
        minutes = _round(value.minute, quarter)

    return time(value.hour, minutes)


def round_next_quarter(value: time) -> time:
    """Rounds the time to the next quarter.

    Args:
        value (time): Time that should be rounded

    Returns:
        [type]: Rounded time to the next quarter
    """

    quarter = 15
    remainder = value.minute % quarter
    if remainder > 5:
        minutes = _round(value.minute + quarter, quarter)
    else:
        minutes = _round(value.minute, quarter)

    hours = value.hour
    if minutes == 60:
        minutes = 0
        hours = hours + 1 if hours != 23 else 0

    return time(hours, minutes)


def _round(value: int, resolution: int) -> int:
    return resolution * (value // resolution)
