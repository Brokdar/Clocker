"""This module creates all types of statistical information about WorkDays"""

import logging
from dataclasses import dataclass
from datetime import date, timedelta

from clocker.model import AbsenceType, WorkDay
from clocker.settings import Settings


@dataclass
class DayCount:
    """Count of the different types of days"""

    work: int = 0
    vacation: int = 0
    flex: int = 0
    sick: int = 0

@dataclass
class Statistics:
    """Model for storing statistics about a set of WorkDays"""

    count: DayCount = DayCount()
    working_hours: timedelta = timedelta(0)
    flextime: timedelta = timedelta(0)
    accessable_vacation_days: int = 0
    target_working_days: int = 0
    target_working_hours: timedelta = timedelta(0)


class StatisticHandler:
    """Class for managing the work time data"""

    def __init__(self, settings: Settings):
        self.__settings = settings

    def collect(self, data: list[WorkDay]) -> Statistics:
        """Collects all type of statistical information about the given set of data

        Args:
            data (list[WorkDay]): data set to be analyzed

        Raises:
            ValueError: data set is not from the same year

        Returns:
            Statistics: statistic object containing all information
        """

        statistics = Statistics()

        working_hours = self.__settings.read('Work', 'WorkingHours')
        statistics.accessable_vacation_days = self.__settings.read('Work', 'VacationDays')

        if not data:
            return statistics

        if data[0].date.year != data[-1].date.year:
            raise ValueError(f'data set is not from the same year: {data[0].date.year} != {data[-1].date.year}')

        first_day = date(data[0].date.year, 1, 1)
        last_day = data[-1].date
        statistics.target_working_days = _count_workdays(first_day, last_day)

        for workday in data:
            self.__count(workday, statistics.count)

            if workday.absence == AbsenceType.WORKDAY:
                statistics.working_hours += workday.duration
            elif workday.absence == AbsenceType.HOLIDAY:
                if _is_weekday(workday.date):
                    statistics.target_working_days -= 1
            elif workday.absence != AbsenceType.FLEXDAY:
                statistics.working_hours += working_hours

        statistics.target_working_hours = timedelta(seconds=statistics.target_working_days * working_hours.total_seconds())
        statistics.flextime = statistics.working_hours - statistics.target_working_hours

        return statistics


    @staticmethod
    def __count(workday: WorkDay, count: DayCount):
        match workday.absence:
            case AbsenceType.WORKDAY:
                count.work += 1
            case AbsenceType.VACATION:
                count.vacation += 1
            case AbsenceType.FLEXDAY:
                count.flex += 1
            case AbsenceType.SICKNESS:
                count.sick += 1
            case AbsenceType.HOLIDAY:
                return
            case _:
                logging.error('Statistics - count: invalid absence type %s', workday.absence)


    def flextime(self, data: WorkDay) -> timedelta:
        """Calculates the flextime for the given day

        Args:
            data (WorkDay): day for which the flextime should be calculated

        Returns:
            timedelta: flextime
        """

        if data.end is None:
            return timedelta(0)
        return data.duration - self.__settings.read('Work', 'WorkingHours')

def _count_workdays(first_day: date, last_day: date) -> int:
    day_generator = (first_day + timedelta(x + 1) for x in range((last_day - first_day).days))
    return sum(_is_weekday(day) for day in day_generator)

def _is_weekday(day: date) -> bool:
    return day.weekday() < 5
