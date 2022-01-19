"""This module is responsible for a visual representation of the model data"""

from datetime import date, datetime

from rich.console import Console
from rich.table import Table

from clocker import database
from clocker.model import WorkDay


def display_day(day: date = datetime.now().date()):
    """Displays a specific workday.

    Args:
        day (date, optional): Date of day to be displayed. Defaults to datetime.now().date().
    """

    console = Console()
    table = _table(f'Working Day - {day.strftime("%a %d.%m.%Y")}')

    workday = database.load(day)
    if workday:
        table.add_row(*_convert(workday))
        console.print(table)
    else:
        console.print(f'No workday found for day: {day}')

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

    console = Console()
    table = _table(f'Working Days - {month:02}/{year}')

    data = database.load_month(month, year)
    for workday in data:
        table.add_row(*_convert(workday))

    console.print(table)

def _convert(workday: WorkDay) -> list:
    return [
        workday.date.strftime("%a %d.%m.%Y"),
        workday.start.strftime("%H:%M:%S") if workday.start is not None else None,
        workday.end.strftime("%H:%M:%S") if workday.end is not None else None,
        str(workday.pause),
        str(workday.duration)
    ]

def _table(title: str):
    table = Table(title=title)
    table.add_column('Date', style='cyan')
    table.add_column('Start')
    table.add_column('End')
    table.add_column('Pause')
    table.add_column('Duration')

    return table
