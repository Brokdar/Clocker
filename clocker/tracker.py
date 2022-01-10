"""This module tracks the working hours"""

from datetime import date, datetime, time, timedelta

from rich.console import Console
from rich.table import Table

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
        # handle error state
        return

    workday.end = now.time()
    database.store(workday)

def track(day: date, start: time, end: time, pause: timedelta):
    """Add a new weekday records to the database with the given values.

    Args:
        day (date): date of the weekday
        start (time): begin of work
        end (time): end of work
        pause (timedelta): duration of pause
    """

    workday = database.load(day)
    if workday is None:
        workday = WorkDay(day, start, end, pause)

    database.store(workday)

def display():
    """Displays all weekday records of the current month."""

    today = datetime.today()
    display_month(today.month, today.year)

def display_month(month: int, year: int):
    """Displays all weekday records for the given month and year.

    Args:
        month (int): month of the records to display
        year (int): years of the records to display
    """

    table = Table(title=f'Working Days - {month:02}/{year}')
    table.add_column('Date', style='cyan')
    table.add_column('Start')
    table.add_column('End')
    table.add_column('Pause')
    table.add_column('Duration')

    data = database.load_month(month, year)
    for workday in data:
        table.add_row(
            workday.date.strftime("%a %d.%m.%Y"),
            workday.start.strftime("%H:%M:%S"),
            workday.end.strftime("%H:%M:%S"),
            str(workday.pause),
            str(workday.duration)
        )

    console = Console()
    console.print(table)
