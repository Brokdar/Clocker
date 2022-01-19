"""This module is responsible for a visual representation of the model data"""

from datetime import datetime

from rich.console import Console
from rich.table import Table

from clocker import database


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
