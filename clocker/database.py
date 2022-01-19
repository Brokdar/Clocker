"""Infrastructure to the database"""

from datetime import date
from typing import Optional

from clocker.model import WorkDay


class Database:
    def __init__(self):
        self.__data = {}

    def store(self, record: WorkDay):
        """Stores a record of a workday into the database.

        Args:
            record (WorkDay): model of a workday
        """

        self.__data[record.date] = record

    def load(self, day: date) -> Optional[WorkDay]:
        """Loads an already stored workday record from the database.

        Args:
            day (date): unique identifier to the workday record

        Returns:
            Optional[WorkDay]: model of a workday or None if not existing
        """

        return self.__data[day] if day in self.__data else None

    def remove(self, day: date) -> bool:
        """Removes an already existing record from the database.

        Args:
            day (date): workday to remove

        Returns:
            bool: True if successful removed else False
        """

        if day in self.__data:
            del self.__data[day]
            return True

        return False

    def load_month(self, month: int, year: int) -> list[WorkDay]:
        """Loads all available records stored in the database for the given month and year.

        Args:
            month (int): month of the workday records
            year (int): year of the workday records

        Returns:
            list[WorkDay]: All found records or an empty list
        """

        return [value for key, value in self.__data.items() if key.month == month and key.year == year]
