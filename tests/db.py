import os

from clocker.database import Database


def get() -> Database:
    db_file = 'db/test.json'
    if os.path.exists(db_file):
        os.remove(db_file)

    return Database(db_file)
