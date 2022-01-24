"""This module is responsible for a visual representation of the model data"""

from datetime import timedelta

from rich.console import Console
from rich.table import Table

from clocker import converter
from clocker.core import TimeManager
from clocker.model import WorkDay, WorkDayStatistics
from clocker.settings import Settings


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
        table = _table(f'Working Day - {converter.date_to_str(day.date)}')

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
            converter.date_to_str(workday.date),
            converter.time_to_str(workday.begin) if workday.begin is not None else None,
            converter.time_to_str(workday.end) if workday.end is not None else None,
            converter.delta_to_str(workday.pause),
            converter.delta_to_str(workday.duration),
            converter.delta_to_str(self.__time_manager.flextime(workday))
        ]

def _display_statistics(console: Console, statistics: WorkDayStatistics):
    console.print(f"On average, you started at [bold]{statistics.avg_begin}[/] and worked until [bold]{statistics.avg_end}[/]")
    console.print(
        f"You have worked a total of [bold]{converter.delta_to_str(statistics.sum_duration)}[/], \
        which is {'more [green ' if statistics.sum_flextime > timedelta(0) else 'less [red '} \
        bold]{converter.delta_to_str(statistics.sum_flextime)}[/] than you're target"
    )

def _table(title: str, statistics: WorkDayStatistics = None):
    table = Table(title=title)
    table.add_column('Date', style='cyan')
    table.add_column('Start')
    table.add_column('End')
    table.add_column('Pause')
    table.add_column('Duration')
    table.add_column('Flextime', justify='right')

    if statistics:
        table.columns[1].footer = converter.time_to_str(statistics.avg_begin)
        table.columns[2].footer = converter.time_to_str(statistics.avg_end)
        table.columns[3].footer = converter.delta_to_str(statistics.avg_pause)
        table.columns[4].footer = converter.delta_to_str(statistics.sum_duration)
        table.columns[5].footer = converter.delta_to_str(statistics.sum_flextime)

    return table
