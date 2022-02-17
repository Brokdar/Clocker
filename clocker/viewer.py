"""This module is responsible for a visual representation of the model data"""

from calendar import Calendar

from rich.console import Console
from rich.style import Style
from rich.table import Table

from clocker import converter
from clocker.model import AbsenceType, WorkDay
from clocker.statistics import StatisticHandler


class Viewer:
    """Viewer class for displaying a single WorkDay or a set of WorkDays"""

    def __init__(self, statistic: StatisticHandler):
        self.__stats = statistic
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
                if data[idx].absence == AbsenceType.HOLIDAY:
                    table.add_row(*self.__convert(data[idx]), style=Style(color='cyan'))
                else:
                    table.add_row(*self.__convert(data[idx]), style=style)
                idx += 1
            else:
                table.add_row(converter.date_to_str(day), style=style)

        self.__console.print(table)

    def display_statistics(self, data: list[WorkDay]):
        """Displays a statistic object

        Args:
            data (list[WorkDay]): data set to be analyzed
        """

        statistics = self.__stats.collect(data)

        self.__console.print(' | '.join([
            f'Vacation {statistics.count.vacation}/{statistics.accessable_vacation_days} ({statistics.accessable_vacation_days - statistics.count.vacation})',  # pylint: disable = line-too-long
            f'Flexday {statistics.count.flex}',
            f'Sickness {statistics.count.sick}',
            f'Flextime {self.__colorize(converter.delta_to_str(statistics.flextime))}'
        ]))

    def __convert(self, workday: WorkDay) -> list:
        if workday.is_absence_day():
            return [converter.date_to_str(workday.date), converter.enum_to_abbreviation(workday.absence)]

        return [
            converter.date_to_str(workday.date),
            converter.enum_to_abbreviation(workday.absence),
            converter.time_to_str(workday.begin) if workday.begin is not None else None,
            converter.time_to_str(workday.end) if workday.end is not None else None,
            converter.delta_to_str(workday.pause),
            converter.delta_to_str(workday.duration),
            converter.delta_to_str(self.__stats.flextime(workday))
        ]

    @staticmethod
    def __colorize(value: str) -> str:
        return f'[red]{value}[/]' if value.startswith('-') else f'[green]{value}[/]'


def _table(title: str):
    table = Table(title=title)
    table.add_column('Date')
    table.add_column('Type', justify='center')
    table.add_column('Start')
    table.add_column('End')
    table.add_column('Pause')
    table.add_column('Duration')
    table.add_column('Flextime', justify='right')

    return table
