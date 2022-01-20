"""This module is responsible for a visual representation of the model data"""

from datetime import date, time, timedelta

from rich.console import Console
from rich.table import Table

from clocker.model import WorkDay
from clocker.settings import Settings


class Viewer:
    def __init__(self, settings: Settings):
        self.__settings = settings

    def display(self, day: WorkDay):
        """Displays a specific WorkDay

        Args:
            day (WorkDay): Workday to be displayed
        """

        console = Console()
        table = _table(f'Working Day - {date_to_str(day.date)}')

        table.add_row(*self.__convert(day))
        console.print(table)


    def display_month(self, month: int, year: int, data: list[WorkDay]):
        """Displays all workday records of the given month and year.

        Args:
            month (int): month of the records to display
            year (int): years of the records to display
            data (list[WorkDay]): all WorkDay records of the month
        """

        console = Console()
        table = _table(f'Working Days - {month:02}/{year}')

        for workday in sorted(data, key=lambda o: o.date):
            table.add_row(*self.__convert(workday))

        console.print(table)

    def __convert(self, workday: WorkDay) -> list:
        return [
            date_to_str(workday.date),
            time_to_str(workday.start) if workday.start is not None else None,
            time_to_str(workday.end) if workday.end is not None else None,
            delta_to_str(workday.pause),
            delta_to_str(workday.duration),
            delta_to_str(workday.duration - self.__settings.read('Workday', 'Duration'))
        ]

def _table(title: str):
    table = Table(title=title)
    table.add_column('Date', style='cyan')
    table.add_column('Start')
    table.add_column('End')
    table.add_column('Pause')
    table.add_column('Duration')
    table.add_column('Flextime', justify='right')

    return table

def date_to_str(value: date) -> str:
    """Returns the string representation of a given date.

    Args:
        date (date): date to be displayed

    Returns:
        str: %a %d.%m.%Y
    """

    return value.strftime("%a %d.%m.%Y")

def time_to_str(value: time) -> str:
    """Returns the string representation of a given time.

    Args:
        time (time): time to be displayed

    Returns:
        str: %H:%M:%S
    """

    return value.strftime("%H:%M:%S")

def delta_to_str(value: timedelta) -> str:
    """Returns the string representation of a given timedelta.

    Args:
        value (timedelta): timedelta to be displayed

    Returns:
        str: negative or positive timedelta
    """

    if value < timedelta(0):
        return '-' + str(-value)
    return str(value)
