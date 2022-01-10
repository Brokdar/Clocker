"""Infrastructure to the database"""

from datetime import date
from typing import Optional

from clocker.model import WorkDay

data = {}

def store(record: WorkDay):
    """Stores a record of a workday into the database.

    Args:
        record (WorkDay): model of a workday
    """

    data[record.date] = record

def load(day: date) -> Optional[WorkDay]:
    """Loads an already stored workday record from the database.

    Args:
        day (date): unique identifier to the workday record

    Returns:
        Optional[WorkDay]: model of a workday or None if not existing
    """

    return data[day] if day in data else None

def load_month(month: int, year: int) -> list[WorkDay]:
    """Loads all available records stored in the database for the given month and year.

    Args:
        month (int): month of the workday records
        year (int): year of the workday records

    Returns:
        list[WorkDay]: All found records or an empty list
    """

    return [value for key, value in data.items() if key.month == month and key.year == year]
