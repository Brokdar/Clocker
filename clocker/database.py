"""Infrastructure to the database"""

from datetime import date, datetime, time, timedelta
from json import JSONEncoder
from typing import Optional

from tinydb import TinyDB, where

from clocker.model import WorkDay


class DateTimeEncoder(JSONEncoder):
    def default(self, o):
        if isinstance(o, (date, time)):
            return o.isoformat()

        if isinstance(o, timedelta):
            return (datetime.min + o).time().isoformat()

        return JSONEncoder.default(self, o)

class Database:
    def __init__(self, file: str):
        self.__db = TinyDB(file, cls=DateTimeEncoder, indent=4)

    def store(self, record: WorkDay):
        """Stores a record of a workday into the database.

        Args:
            record (WorkDay): model of a workday
        """

        self.__db.upsert(record.__dict__, where('date') == record.date.isoformat())

    def load(self, day: date) -> Optional[WorkDay]:
        """Loads an already stored workday record from the database.

        Args:
            day (date): unique identifier to the workday record

        Returns:
            Optional[WorkDay]: model of a workday or None if not existing
        """

        data = self.__db.get(where('date') == day.isoformat())
        if data is not None:
            return WorkDay.decode(data)

        return None

    def remove(self, day: date) -> bool:
        """Removes an already existing record from the database.

        Args:
            day (date): workday to remove

        Returns:
            bool: True if successful removed else False
        """

        self.__db.remove(where('date') == day.isoformat())

    def load_month(self, month: int, year: int) -> list[WorkDay]:
        """Loads all available records stored in the database for the given month and year.

        Args:
            month (int): month of the workday records
            year (int): year of the workday records

        Returns:
            list[WorkDay]: All found records or an empty list
        """

        pattern = f'{year:4}-{month:02}'
        data = self.__db.search(where('date').test(lambda d: d.startswith(pattern)))
        return [WorkDay.decode(item) for item in data]
