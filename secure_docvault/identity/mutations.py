"""Запис облікових записів."""

from __future__ import annotations

from ..persistence.engine import session


def insert_account(
    username: str, email: str, password_hash: str, salt: str, role: str = "user"
) -> int:
    with session() as connection:
        cursor = connection.execute(
            """
            INSERT INTO users (username, email, password_hash, salt, role)
            VALUES (?, ?, ?, ?, ?)
            """,
            (username, email, password_hash, salt, role),
        )
        return int(cursor.lastrowid)
