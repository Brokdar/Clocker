from datetime import datetime, timedelta
from typing import Optional

import click

from clocker import database, tracker, viewer
from clocker.model import WorkDay


@click.command(help='Starts the tracking of the current day')
def start():
    tracker.start()
    viewer.display_day()

@click.command(help='Stops the tracking of the current day')
def stop():
    try:
        tracker.stop()
        viewer.display_day()
    except RuntimeError:
        print(f"[Error] start wasn't called for today: {datetime.now().date().strftime('%a %d.%m.%Y')}")

@click.command(help='Manual tracking of workdays. Can also be used to update values of already tracked days')
@click.option('-d', '--date', required=True, type=str, help='Date of workday in format: dd.mm.yyyy')
@click.option('-s', '--start', type=str, default=None, help='Begin of workday in format: hh:mm')
@click.option('-e', '--end', type=str, default=None, help='End of workday in format: hh:mm')
@click.option('-p', '--pause', type=str, default=None, help='Pause on workday in format: hh:mm')
def track(date: str, start: Optional[str], end: Optional[str], pause: Optional[str]):
    date = datetime.strptime(date, '%d.%m.%Y').date()
    workday = database.load(date)
    if workday is None:
        workday = WorkDay(date)

    if start is not None:
        workday.start = datetime.strptime(start, '%H:%M').time()

    if end is not None:
        workday.end = datetime.strptime(end, '%H:%M').time()

    if pause is not None:
        time = datetime.strptime(pause, '%H:%M').time()
        workday.pause = timedelta(hours=time.hour, minutes=time.minute)

    try:
        tracker.track(workday.date, workday.start, workday.end, workday.pause)
        viewer.display_day(workday.date)
    except ValueError:
        print(f"[Error] start must be set for workday: {date.strftime('%a %d.%m.%Y')}")


@click.command(help='Displays all tracked workdays of the given month and year')
@click.option('-m', '--month', type=int, default=datetime.now().date().month, help='Month to show, defaults to current month')
@click.option('-y', '--year', type=int, default=datetime.now().date().year, help='Year to show, defaults to current year')
def show(month: int, year: int):
    viewer.display_month(month, year)
