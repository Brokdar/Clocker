"""This module is responsible for a visual representation of the model data"""

from calendar import Calendar
from datetime import timedelta

from rich.console import Console
from rich.style import Style
from rich.table import Table

from clocker import converter
from clocker.core import TimeManager
from clocker.model import WorkDay
from clocker.settings import Settings


class Viewer:
    """Viewer class for displaying a single WorkDay or a set of WorkDays"""

    def __init__(self, settings: Settings):
        self.__time_manager = TimeManager(settings)
        self.__console = Console()

    def display(self, day: WorkDay):
        """Displays a specific WorkDay

        Args:
            day (WorkDay): Workday to be displayed
        """

        table = _table(f'Working Day - {converter.date_to_str(day.date)}')
        table.add_row(*self.__convert(day))

        self.__console.print(table)

    def display_month(self, month: int, year: int, data: list[WorkDay]):
        """Displays all workday records of the given month and year.

        Args:
            month (int): month of the records to display
            year (int): years of the records to display
            data (list[WorkDay]): all WorkDay records of the month
        """

        table = _table(f'Working Days - {month:02}/{year}')
        data.sort(key=lambda o: o.date)

        cal = Calendar()
        idx = 0
        for day in cal.itermonthdates(year, month):
            if day.month != month or day.year != year:
                continue

            style = Style()
            if day.weekday() >= 5:
                style += Style(color='grey42')

            if idx < len(data) and day == data[idx].date:
                table.add_row(*self.__convert(data[idx]), style=style)
                idx += 1
            else:
                table.add_row(converter.date_to_str(day), style=style)

        self.__console.print(table)
        self.__display_statistics(data)

    def __convert(self, workday: WorkDay) -> list:
        return [
            converter.date_to_str(workday.date),
            converter.time_to_str(workday.begin) if workday.begin is not None else None,
            converter.time_to_str(workday.end) if workday.end is not None else None,
            converter.delta_to_str(workday.pause),
            converter.delta_to_str(workday.duration),
            converter.delta_to_str(self.__time_manager.flextime(workday))
        ]

    def __display_statistics(self, data: list[WorkDay]):
        statistics = self.__time_manager.statistics(data)

        self.__console.print(
            f"On average, you started at [bold]{converter.time_to_str(statistics.avg_begin)}[/] and worked until [bold]{converter.time_to_str(statistics.avg_end)}[/]"
        )
        self.__console.print(f"You have worked a total of [bold]{converter.delta_to_str(statistics.sum_duration)}[/], \
which is {'more [green ' if statistics.sum_flextime >= timedelta(0) else 'less [red '} \
bold]{converter.delta_to_str(statistics.sum_flextime)}[/] than you're target")


def _table(title: str):
    table = Table(title=title)
    table.add_column('Date')
    table.add_column('Start')
    table.add_column('End')
    table.add_column('Pause')
    table.add_column('Duration')
    table.add_column('Flextime', justify='right')

    return table
