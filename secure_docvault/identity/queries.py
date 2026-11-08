"""Читання облікових записів.

Кожен запит — окремий текст із плейсхолдерами ``?``. Дані користувача
ніколи не склеюються з SQL.
"""

from __future__ import annotations

from ..persistence.engine import one


def by_username(username: str) -> dict | None:
    row = one(
        """
        SELECT id, username, email, password_hash, salt, role, created_at,
               is_active
          FROM users
         WHERE username = ?
        """,
        (username,),
    )
    return dict(row) if row else None


def by_email(email: str) -> dict | None:
    row = one(
        """
        SELECT id, username, email, password_hash, salt, role, created_at,
               is_active
          FROM users
         WHERE email = ?
        """,
        (email,),
    )
    return dict(row) if row else None


def by_id(account_id: int) -> dict | None:
    row = one(
        """
        SELECT id, username, email, password_hash, salt, role, created_at,
               is_active
          FROM users
         WHERE id = ?
        """,
        (account_id,),
    )
    return dict(row) if row else None
