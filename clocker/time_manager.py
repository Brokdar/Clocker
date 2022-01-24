"""Contains utility functions for handling work time data."""

from datetime import datetime, time, timedelta

from clocker.model import WorkDay, WorkDayStatistics
from clocker.settings import Settings


class TimeManager:
    """Class for managing the work time data"""

    def __init__(self, settings: Settings):
        self.__settings = settings

    def statistics(self, data: list[WorkDay]) -> WorkDayStatistics:
        """Evaluates statistics of a given list of WorkDay objects

        Args:
            data (list[WorkDay]): list of WorkDay objects

        Returns:
            WorkDayStatistics: Statistical information about the list of WorkDay
        """
        
        statistics = WorkDayStatistics()

        avg_start = timedelta(0)
        avg_end = timedelta(0)

        for day in data:
            avg_start = _add(avg_start, day.start)
            avg_end = _add(avg_end, day.end)
            statistics.avg_pause += day.pause
            statistics.sum_duration += day.duration
            statistics.sum_flextime += self.flextime(day)

        avg_start = avg_start / len(data)
        avg_end = avg_end / len(data)
        statistics.avg_pause /= len(data)

        statistics.avg_start = (datetime.min + avg_start).time()
        statistics.avg_end = (datetime.min + avg_end).time()

        return statistics

    def flextime(self, data: WorkDay) -> timedelta:
        """Calculates the flextime for the given day

        Args:
            data (WorkDay): day for which the flextime should be calculated

        Returns:
            timedelta: flextime
        """

        return data.duration - self.__settings.read('Workday', 'Duration')

def _add(left: timedelta, right: time) -> timedelta:
    return left + timedelta(hours=right.hour, minutes=right.minute, seconds=right.second)
