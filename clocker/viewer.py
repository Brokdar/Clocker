"""This module is responsible for a visual representation of the model data"""

from datetime import date, time, timedelta

from rich.console import Console
from rich.table import Table

from clocker.model import WorkDay, WorkDayStatistics
from clocker.settings import Settings
from clocker.time_manager import TimeManager


class Viewer:
    """Viewer class for displaying a single WorkDay or a set of WorkDays"""
    
    def __init__(self, settings: Settings):
        self.__time_manager = TimeManager(settings)

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
        _display_statistics(console, self.__time_manager.statistics(data))

    def __convert(self, workday: WorkDay) -> list:
        return [
            date_to_str(workday.date),
            time_to_str(workday.start) if workday.start is not None else None,
            time_to_str(workday.end) if workday.end is not None else None,
            delta_to_str(workday.pause),
            delta_to_str(workday.duration),
            delta_to_str(self.__time_manager.flextime(workday))
        ]

def _display_statistics(console: Console, statistics: WorkDayStatistics):
    console.print(f"On average you began to work at [bold]{statistics.avg_start}[/] and left at [bold]{statistics.avg_end}[/]")
    console.print(f"You have worked a total of [bold]{delta_to_str(statistics.sum_duration)}[/], which is {'more' if statistics.sum_flextime > timedelta(0) else 'less'} [bold]{delta_to_str(statistics.sum_flextime)}[/] than you're target")

def _table(title: str, statistics: WorkDayStatistics = None):
    table = Table(title=title)
    table.add_column('Date', style='cyan')
    table.add_column('Start')
    table.add_column('End')
    table.add_column('Pause')
    table.add_column('Duration')
    table.add_column('Flextime', justify='right')

    if statistics:
        table.columns[1].footer = time_to_str(statistics.avg_start)
        table.columns[2].footer = time_to_str(statistics.avg_end)
        table.columns[3].footer = delta_to_str(statistics.avg_pause)
        table.columns[4].footer = delta_to_str(statistics.sum_duration)
        table.columns[5].footer = delta_to_str(statistics.sum_flextime)

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
        return '-' + _convert_delta(-value)
    return _convert_delta(value)

def _convert_delta(value: timedelta) -> str:
    total_seconds = int(value.total_seconds())
    seconds = total_seconds % 60
    minutes = (total_seconds // 60) % 60
    hours = (total_seconds // 3600)

    return f'{hours}:{minutes:02}:{seconds:02}'
