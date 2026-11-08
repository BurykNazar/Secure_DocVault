"""З'єднання з SQLite та елементарні запити.

Кожна операція відкриває власне з'єднання й завершується або комітом,
або відкатом — «напівзаписаних» даних не буває.
"""

from __future__ import annotations

import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager

from ..settings import settings


@contextmanager
def session() -> Iterator[sqlite3.Connection]:
    settings.database.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(settings.database, timeout=15.0)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    connection.execute("PRAGMA busy_timeout = 5000")
    connection.execute("PRAGMA journal_mode = WAL")

    try:
        yield connection
        connection.commit()
    except BaseException:
        connection.rollback()
        raise
    finally:
        connection.close()


def one(sql: str, values: tuple[object, ...] = ()) -> sqlite3.Row | None:
    with session() as connection:
        return connection.execute(sql, values).fetchone()


def scalar(sql: str, values: tuple[object, ...] = ()) -> int:
    row = one(sql, values)
    return int(row[0]) if row else 0
