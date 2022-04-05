"""This module tracks the working hours"""

import logging
from datetime import date, datetime, time, timedelta
from typing import Generator, Optional

from clocker.database import Database
from clocker.model import AbsenceType, WorkDay
from clocker.settings import Settings


class SettingsError(Exception):
    """Custom Exception for signaling errors related to settings"""


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
        if self._disallowed_tracking_on_sundays(now.date()):
            raise SettingsError(f'start ({now.date()}) - auto tracking is disabled on sundays')

        workday = self.__db.load(now.date())
        if workday:
            if self._disallowed_tracking_on_holidays(workday):
                raise SettingsError(f'start({workday.date}) - auto tracking is disabled on holidays')

            logging.info('start (%s) - workday is already present in database', now.date())
            return workday

        if self.__settings.read('Behavior', 'RoundToQuarter'):
            begin = round_prev_quarter(now.time())
            logging.debug('start (%s) - round to previous quarter (%s -> %s)', now.date(), now.time(), begin)
        else:
            begin = now.replace(microsecond=0).time()

        workday = WorkDay(date=now.date(), begin=begin)

        self.__db.store(workday)
        logging.info('start (%s) - start tracking %s', workday.date, workday)

        return workday

    def stop(self) -> WorkDay:
        """Stops the tracking of working hours for the current day. Sets end time to current time.

        Raises:
            RuntimeError: raised if stop has been called before start

        Returns:
            WorkDay: workday model with the input values set
        """

        now = datetime.now()
        if self._disallowed_tracking_on_sundays(now.date()):
            raise SettingsError(f'stop ({now.date()}) - auto tracking is disabled on sundays')

        workday = self.__db.load(now.date())
        if workday is None:
            raise RuntimeError(f"stop ({now.date()}) - 'start' must be called before 'stop'")

        if self._disallowed_tracking_on_holidays(workday):
            raise SettingsError(f'stop ({workday.date}) - auto tracking is disabled on holidays')

        if self.__settings.read('Behavior', 'RoundToQuarter'):
            end = round_next_quarter(now.time())
            logging.debug('stop (%s) - round to next quarter (%s -> %s)', workday.date, now.time(), end)
        else:
            end = now.replace(microsecond=0).time()

        updated = False
        if workday.end:
            if end <= workday.end:
                logging.info('stop (%s) - time is less or equal to tracked time (%s <= %s)', workday.date, end, workday.end)
                return workday

            updated = True
            old_end = workday.end

        workday.end = end
        self.__set_pause(workday)
        self.__db.store(workday)

        if updated:
            logging.info('stop (%s) - update end time (%s -> %s)', workday.date, old_end, end)
        else:
            logging.info('stop (%s) - stop tracking %s', now.date(), workday)

        return workday

    def _disallowed_tracking_on_sundays(self, day: date) -> bool:
        return day.weekday() == 6 and self.__settings.read('Behavior', 'DisableAutoTrackingOnSundays')

    def _disallowed_tracking_on_holidays(self, workday: WorkDay) -> bool:
        return workday.absence == AbsenceType.HOLIDAY and self.__settings.read('Behavior', 'DisableAutoTrackingOnHolidays')

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
            workday = WorkDay(date=day)
            logging.info('track (%s) - create new workday', workday.date)
        else:
            logging.info('track (%s) - update %s', workday.date, workday)

        workday.begin = begin or workday.begin
        workday.end = end or workday.end
        workday.pause = pause or workday.pause

        if workday.pause == timedelta(0):
            self.__set_pause(workday)

        if workday.begin is None:
            raise ValueError(f'track ({workday.date}) - begin value is None')

        self.__db.store(workday)
        logging.info('track (%s) - set %s', workday.date, workday)

        return workday

    def __set_pause(self, workday: WorkDay):
        if workday.pause > timedelta(0):
            return

        if workday.end is not None:
            if workday.duration > timedelta(hours=6):
                pause = self.__settings.read('Work', 'DefaultPauseTime')
                if pause:
                    workday.pause = pause
                    logging.debug('pause (%s) - apply default pause time from settings: %s', workday.date, pause)
                else:
                    logging.warning("pause (%s) - no 'DefaultPauseTime' is configured in settings", workday.date)
            else:
                logging.debug('pause (%s) - no pause time set because duration is less than 6 hours', workday.date)
        else:
            logging.debug('pause (%s) - no pause time set because was end time not provided', workday.date)

    def remove(self, day: date):
        """Remove a WorkDay from the database

        Args:
            day (date): Date of WorkDay

        Raises:
            ValueError: Unexpected error while remove the WorkDay from the database
        """

        workday = self.__db.load(day)
        if workday is None:
            logging.info('remove (%s) - no workday found', day)
            return

        if self.__db.remove(day):
            logging.info('remove (%s) - removed %s', day, workday)
        else:
            raise ValueError(f'failed removing workday({day}) from database')

    def notify(self, start: date, end: date, absence_type: AbsenceType) -> list[WorkDay]:
        """Notify about an absence period

        Args:
            start (date): Start date of the absence period
            end (date): End date of absence period
            absence_type (AbsenceType): Absence Type

        Returns:
            list[WorkDay]: workdays with set absence type
        """

        workdays = []
        for day in iter_workdays(start, end):
            workday = self.__db.load(day)
            if workday is not None:
                if workday.absence == AbsenceType.HOLIDAY:
                    continue  # holidays aren't supposed to be overwritten

                logging.info('notify (%s) - overriding %s', workday.date, workday)

            workday = WorkDay(date=day, absence=absence_type)
            workdays.append(workday)
            self.__db.store(workday)

            logging.info('notify (%s) - absence %s', workday.date, workday.absence)

        return workdays


def iter_workdays(start: date, end: date) -> Generator[date, None, None]:
    for n in range(int((end - start).days) + 1):
        day = start + timedelta(days=n)
        if day.weekday() < 5:  # only workdays
            yield day


def round_prev_quarter(value: time) -> time:
    """Rounds the current time to the previous quarter of an hour.

    The time is rounded when the current minutes are no more than 10 minutes from the previous quarter of an hour.
    Otherwise, it is rounded up to the nearest quarter of an hour.

    - current time = 8:30, rounded = 8:30
    - current time = 8:40, rounded = 8:30
    - current time = 8:41, rounded = 8:45

    Args:
        value (time): Time that should be rounded

    Returns:
        [type]: Rounded time to the previous quarter
    """

    return _round_quarter(value, 10)


def round_next_quarter(value: time) -> time:
    """Rounds the current time to the next quarter of an hour.

    The time is rounded when the current minutes are no more than 10 minutes from the next quarter of an hour.
    Otherwise, it is rounded up to the nearest quarter of an hour.

    - current time = 8:30, rounded = 8:30
    - current time = 8:35, rounded = 8:30
    - current time = 8:36, rounded = 8:45

    Args:
        value (time): Time that should be rounded

    Returns:
        [type]: Rounded time to the next quarter
    """

    return _round_quarter(value, 5)


def _round_quarter(value: time, threshold: int) -> time:
    quarter = 15
    remainder = value.minute % quarter

    minutes = _round(value.minute + quarter, quarter) if remainder > threshold else _round(value.minute, quarter)
    return _advance_time(value.hour, minutes)


def _round(value: int, resolution: int) -> int:
    return resolution * (value // resolution)


def _advance_time(hours: int, minutes: int) -> time:
    if minutes == 60:
        minutes = 0
        hours = hours + 1 if hours != 23 else 0

    return time(hours, minutes)
