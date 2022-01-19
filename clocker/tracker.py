"""This module tracks the working hours"""

from datetime import date, datetime, time, timedelta

from clocker import database
from clocker.model import WorkDay


def start():
    """Starts tracking of working hours for the current day. Sets start time to current time"""

    now = datetime.now()
    workday = WorkDay(now.date(), now.time(), None, timedelta(minutes=30))
    database.store(workday)

def stop():
    """Stops the tracking of working hours for the current day. Sets end time to current time."""

    now = datetime.now()
    workday = database.load(now.date())
    if workday is None:
        raise RuntimeError('[Error] start() must be called before stop()')

    workday.end = now.time()
    database.store(workday)

def track(day: date, begin: time, end: time, pause: timedelta):
    """Add a new weekday records to the database with the given values.

    Args:
        day (date): date of the weekday
        begin (time): begin of work
        end (time): end of work
        pause (timedelta): duration of pause
    """

    workday = database.load(day)
    if workday is None:
        workday = WorkDay(day, begin, end, pause)
    else:
        workday.start = begin
        workday.end = end
        workday.pause = pause

    database.store(workday)
