import shutil
from pathlib import Path

from clocker.database import Database

db_dir = Path('tests/db')


def get() -> Database:
    if exists():
        cleanup()

    return Database(db_dir)


def exists() -> bool:
    return db_dir.exists()


def cleanup():
    shutil.rmtree(db_dir)
