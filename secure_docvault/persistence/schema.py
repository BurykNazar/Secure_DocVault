"""Версійована схема бази даних.

На старті застосунок застосовує лише ті міграції, яких ще немає в
schema_history. Повторний запуск нічого не змінює.
"""

from __future__ import annotations

import logging

from .engine import session

log = logging.getLogger("vault.schema")

VERSION = 1

MIGRATIONS: dict[int, tuple[str, ...]] = {
    1: (
        """
        CREATE TABLE IF NOT EXISTS users (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            username        TEXT    NOT NULL UNIQUE COLLATE NOCASE,
            email           TEXT    NOT NULL UNIQUE COLLATE NOCASE,
            password_hash   TEXT    NOT NULL,
            salt            TEXT    NOT NULL,
            role            TEXT    NOT NULL DEFAULT 'user'
                                    CHECK (role IN ('user', 'admin')),
            created_at      TEXT    NOT NULL
                                    DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
            is_active       INTEGER NOT NULL DEFAULT 1
                                    CHECK (is_active IN (0, 1)),
            failed_attempts INTEGER NOT NULL DEFAULT 0,
            locked_until    TEXT
        )
        """,
        "CREATE INDEX IF NOT EXISTS users_email ON users (email)",
        "CREATE INDEX IF NOT EXISTS users_state ON users (is_active, locked_until)",
    ),
}


def _installed_version() -> int:
    with session() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS schema_history (
                version    INTEGER PRIMARY KEY,
                applied_at TEXT NOT NULL
                        DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))
            )
            """
        )
        row = connection.execute("SELECT MAX(version) FROM schema_history").fetchone()
    return int(row[0] or 0)


def install() -> None:
    current = _installed_version()
    for version in range(current + 1, VERSION + 1):
        with session() as connection:
            for statement in MIGRATIONS[version]:
                connection.execute(statement)
            connection.execute(
                "INSERT INTO schema_history (version) VALUES (?)", (version,)
            )
        log.info("Схему бази даних оновлено до версії %s", version)
