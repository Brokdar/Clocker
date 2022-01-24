from datetime import datetime
from typing import Optional

import click

from clocker import converter
from clocker.core import Tracker
from clocker.database import Database
from clocker.settings import Settings
from clocker.viewer import Viewer

settings = Settings('settings.ini')
database = Database(settings.read('Database', 'Path'))

@click.command(help='Starts the time tracking for the current day')
def start():
    """Command for starting the time tracking for the current day."""

    tracker = Tracker(settings, database)
    viewer = Viewer(settings)

    workday = tracker.start()
    viewer.display(workday)

@click.command(help='Stops the time tracking for the current day')
def stop():
    """Command for stopping the time tracking for the current day."""

    tracker = Tracker(settings, database)
    viewer = Viewer(settings)

    try:
        workday = tracker.stop()
        viewer.display(workday)
    except RuntimeError:
        print(f"[Error] command start wasn't called for today: {converter.date_to_str(datetime.now().date())}")

@click.command(help='Manual tracking of workdays. Can also be used to update values of already tracked days')
@click.option('-d', '--date', required=True, type=str, help='Date of workday in format: dd.mm.yyyy')
@click.option('-b', '--begin', type=str, default=None, help='Start time of workday in format: hh:mm[:ss]')
@click.option('-e', '--end', type=str, default=None, help='End time of workday in format: hh:mm[:ss]')
@click.option('-p', '--pause', type=str, default=None, help='Pause time on workday in format: hh:mm[:ss]')
def track(date: str, begin: Optional[str], end: Optional[str], pause: Optional[str]):
    """Command for manual tracking time for a given workday.

    Args:
        date (str): Date of the workday
        begin (Optional[str]): Start time of workday
        end (Optional[str]): End time of workday
        pause (Optional[str]): Pause time of workday
    """

    tracker = Tracker(settings, database)
    viewer = Viewer(settings)

    data = [
        converter.str_to_date(date),
        converter.str_to_time(begin) if begin is not None else None,
        converter.str_to_time(end) if end is not None else None,
        converter.str_to_delta(pause) if pause is not None else None
    ]

    try:
        workday = tracker.track(*data)
        viewer.display(workday)
    except ValueError:
        print(f"[Error] start must be set for workday: {converter.date_to_str(workday.date)}")


@click.command(help='Displays all tracked workdays of the given month and year')
@click.option('-m', '--month', type=int, default=datetime.now().date().month, help='Month to show, defaults to current month')
@click.option('-y', '--year', type=int, default=datetime.now().date().year, help='Year to show, defaults to current year')
def show(month: int, year: int):
    viewer = Viewer(settings)

    data = database.load_month(month, year)
    viewer.display_month(month, year, data)
