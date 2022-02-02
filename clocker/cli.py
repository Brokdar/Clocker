"""Command Line Interface of Clocker"""

import logging
from datetime import datetime
from typing import Optional

import click

from clocker import converter
from clocker.core import SettingsError, Tracker
from clocker.database import Database
from clocker.model import AbsenceType
from clocker.settings import Settings
from clocker.viewer import Viewer

settings = Settings('settings.ini')
database = Database(settings.read('Database', 'Path'))


def error(msg: str):
    """Utility function for printing an error message and also log it

    Args:
        msg (str): Error message
    """

    print(f'[Error] {msg}')
    logging.error(msg)


def warning(msg: str):
    """Utility function for print an warning message and also log it

    Args:
        msg (str): Warning message
    """

    print(f'[Warning] {msg}')
    logging.warning(msg)


@click.command(help='Starts the time tracking for the current day')
def start():
    """Command for starting the time tracking for the current day."""

    tracker = Tracker(settings, database)
    viewer = Viewer(settings)

    try:
        workday = tracker.start()
        viewer.display(workday)
    except SettingsError as err:
        warning(err)


@click.command(help='Stops the time tracking for the current day')
def stop():
    """Command for stopping the time tracking for the current day."""

    tracker = Tracker(settings, database)
    viewer = Viewer(settings)

    try:
        workday = tracker.stop()
        viewer.display(workday)
    except RuntimeError as err:
        error(err)
    except SettingsError as err:
        warning(err)


@click.command(help='Manual tracking of workdays, can be used to update values')
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
    except ValueError as err:
        error(err)


@click.command(help='Remove a workday from database')
@click.option('-d', '--date', required=True, type=str, help='Date of workday in format: dd.mm.yyyy')
def remove(date: str):
    """Command for removing a workday from the database

    Args:
        date (str): Date of the workday
    """

    tracker = Tracker(settings, database)

    try:
        tracker.remove(converter.str_to_date(date))
    except ValueError as err:
        error(err)


@click.command(help='Displays all tracked workdays of the given month and year')
@click.option('-m', '--month', type=int, default=datetime.now().date().month, help='Month to show, defaults to current month')
@click.option('-y', '--year', type=int, default=datetime.now().date().year, help='Year to show, defaults to current year')
def show(month: int, year: int):
    """Command for showing all workdays of the given month and year.

    Args:
        month (int): Month to display
        year (int): Year to display
    """

    viewer = Viewer(settings)

    monthly_data = database.load_month(month, year)
    viewer.display_month(month, year, monthly_data)

    data = []
    if monthly_data:
        data = database.all_until(monthly_data[-1].date)

    viewer.display_statistics(data)


@click.command(help='Notifies about an absence day')
@click.option('-d', '--date', required=True, type=str, help='Date of workday in format: dd.mm.yyyy')
@click.option('-a',
              '--absence',
              required=True,
              type=str,
              help='Absence type: W=Workday, V=Vacation, F=Flexday, S=Sickness, H=Holiday')
def notify(date: str, absence: str):
    """Command for notifying about an absence day.

    Args:
        date (str): Date of absence day
        absence (int): Type of absence day
    """

    tracker = Tracker(settings, database)
    viewer = Viewer(settings)

    try:
        absence_type = AbsenceType.from_abbreviation(absence)
        workday = tracker.notify(converter.str_to_date(date), absence_type)
        viewer.display(workday)
    except ValueError as err:
        error(err)


@click.command(help='Updates public holidays of a given year')
@click.option('-y',
              '--year',
              required=True,
              type=int,
              default=datetime.now().date().year,
              help='Year of which the public holidays should be set')
def holidays(year: int):
    """Updates the public holidays of the given year

    Args:
        year (int): year of the holidays
    """

    database.update_public_holidays(year)
