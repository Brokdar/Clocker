"""Infrastructure to the database"""

from datetime import date, datetime, time, timedelta
from json import JSONEncoder
from pathlib import Path
from typing import Optional, Union

from tinydb import TinyDB
from tinydb.table import Document, Table

from clocker.model import AbsenceType, WorkDay


class WorkDayEncoder(JSONEncoder):
    """JSONEncoder for handling datetime objects.

    Args:
        JSONEncoder ([type]): JSONEncoder base class
    """

    def default(self, o):
        if isinstance(o, (date, time)):
            return o.isoformat()

        if isinstance(o, timedelta):
            return (datetime.min + o).time().isoformat()

        if isinstance(o, AbsenceType):
            return o.value

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

    def __init__(self, directory: Union[Path, str]):
        if isinstance(directory, str):
            self.__dir = Path(directory)
        elif isinstance(directory, Path):
            self.__dir = directory
        else:
            raise TypeError(f'[Error] directory is not of type Path or string: {directory}[{type(directory)}]')

        if not self.__dir.exists():
            self.__dir.mkdir(parents=True, exist_ok=True)

        self.__tables = {}

    def __table(self, year: int) -> Table:
        if year in self.__tables:
            return self.__tables[year]

        file = self.__dir.joinpath(f'{year}.json')
        table = TinyDB(file.as_posix(), cls=WorkDayEncoder, indent=4, sort_keys=True).table('workdays')
        table.document_id_class = date.fromisoformat

        self.__tables[year] = table

        return table

    def store(self, record: WorkDay):
        """Stores a record of a workday into the database.

        Args:
            record (WorkDay): model of a workday
        """

        table = self.__table(record.date.year)

        if self.load(record.date):
            table.update(WorkDayDocument(record), doc_ids=[record.date])
        else:
            table.insert(WorkDayDocument(record))

    def load(self, day: date) -> Optional[WorkDay]:
        """Loads an already stored workday record from the database.

        Args:
            day (date): unique identifier to the workday record

        Returns:
            Optional[WorkDay]: model of a workday or None if not existing
        """

        data = self.__table(day.year).get(doc_id=day)
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

        return bool(self.__table(day.year).remove(doc_ids=[day]))

    def load_month(self, month: int, year: int) -> list[WorkDay]:
        """Loads all available records stored in the database for the given month and year.

        Args:
            month (int): month of the workday records
            year (int): year of the workday records

        Returns:
            list[WorkDay]: All found records or an empty list
        """

        data = [
            value for value in self.__table(year).all()
            # value.doc_id is overridden by date object, type hints will show it as int
            if value.doc_id.month == month and value.doc_id.year == year
        ]

        return [WorkDay.decode(item) for item in data]

    def all_until(self, end: date):
        """Loads all available records of end.year stored in the database up until end date.

        Args:
            end (date): end date up until the data should be received

        Returns:
            [type]: All stored records of end.year up until end date
        """

        data = [value for value in self.__table(end.year).all() if value.doc_id <= end]

        return [WorkDay.decode(item) for item in data]
