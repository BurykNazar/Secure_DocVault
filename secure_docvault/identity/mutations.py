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


def save_failure(
    account_id: int, attempts: int, locked_until: str | None
) -> None:
    with session() as connection:
        connection.execute(
            "UPDATE users SET failed_attempts = ?, locked_until = ? WHERE id = ?",
            (attempts, locked_until, account_id),
        )


def clear_failures(account_id: int) -> None:
    with session() as connection:
        connection.execute(
            "UPDATE users SET failed_attempts = 0, locked_until = NULL WHERE id = ?",
            (account_id,),
        )
