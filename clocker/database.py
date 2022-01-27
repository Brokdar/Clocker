"""Infrastructure to the database"""

from datetime import date, datetime, time, timedelta
from json import JSONEncoder
from typing import Optional

from tinydb import TinyDB
from tinydb.table import Document

from clocker.model import WorkDay


class DateTimeEncoder(JSONEncoder):
    """JSONEncoder for handling datetime objects.

    Args:
        JSONEncoder ([type]): JSONEncoder base class
    """

    def default(self, o):
        if isinstance(o, (date, time)):
            return o.isoformat()

        if isinstance(o, timedelta):
            return (datetime.min + o).time().isoformat()

        return JSONEncoder.default(self, o)


class WorkDayDocument(Document):
    """Custom Document for TinyDB tables.

    Args:
        Document ([type]): Document base class of TinyDB
    """

    def __init__(self, value: WorkDay):
        super().__init__(value.encode(), value.date)


class Database:
    """Class for handling JSON database file"""

    def __init__(self, file: str):
        self.__db = TinyDB(file, cls=DateTimeEncoder, indent=4, sort_keys=True)
        self.__table = self.__db.table('workdays')
        self.__table.document_id_class = date.fromisoformat

    def store(self, record: WorkDay):
        """Stores a record of a workday into the database.

        Args:
            record (WorkDay): model of a workday
        """

        if self.load(record.date):
            self.__table.update(WorkDayDocument(record), doc_ids=[record.date])
        else:
            self.__table.insert(WorkDayDocument(record))

    def load(self, day: date) -> Optional[WorkDay]:
        """Loads an already stored workday record from the database.

        Args:
            day (date): unique identifier to the workday record

        Returns:
            Optional[WorkDay]: model of a workday or None if not existing
        """

        data = self.__table.get(doc_id=day)
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

        return bool(self.__table.remove(doc_ids=[day]))

    def load_month(self, month: int, year: int) -> list[WorkDay]:
        """Loads all available records stored in the database for the given month and year.

        Args:
            month (int): month of the workday records
            year (int): year of the workday records

        Returns:
            list[WorkDay]: All found records or an empty list
        """

        data = [
            value for value in self.__table.all()
            # value.doc_id is overridden by date object, type hints will show it as int
            if value.doc_id.month == month and value.doc_id.year == year
        ]

        return [WorkDay.decode(item) for item in data]
