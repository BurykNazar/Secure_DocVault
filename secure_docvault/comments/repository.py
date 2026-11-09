"""SQL для коментарів.

Кожен запит, крім створення, містить умову ``owner_id = ?`` — чужі
записи неможливо ані прочитати, ані змінити, ані видалити.
"""

from __future__ import annotations

from ..persistence.engine import session


def create(owner_id: int, title: str, body: str) -> dict:
    with session() as connection:
        cursor = connection.execute(
            "INSERT INTO comments (owner_id, title, body) VALUES (?, ?, ?)",
            (owner_id, title, body),
        )
        row = connection.execute(
            """
            SELECT id, owner_id, title, body, created_at, updated_at
              FROM comments WHERE id = ?
            """,
            (int(cursor.lastrowid),),
        ).fetchone()
    return dict(row)


def list_for(owner_id: int) -> list[dict]:
    with session() as connection:
        rows = connection.execute(
            """
            SELECT id, owner_id, title, body, created_at, updated_at
              FROM comments WHERE owner_id = ? ORDER BY id DESC
            """,
            (owner_id,),
        ).fetchall()
    return [dict(row) for row in rows]


def get_for(owner_id: int, comment_id: int) -> dict | None:
    with session() as connection:
        row = connection.execute(
            """
            SELECT id, owner_id, title, body, created_at, updated_at
              FROM comments WHERE id = ? AND owner_id = ?
            """,
            (comment_id, owner_id),
        ).fetchone()
    return dict(row) if row else None


def update(owner_id: int, comment_id: int, title: str, body: str) -> dict | None:
    with session() as connection:
        cursor = connection.execute(
            """
            UPDATE comments
               SET title = ?, body = ?, updated_at = CURRENT_TIMESTAMP
             WHERE id = ? AND owner_id = ?
            """,
            (title, body, comment_id, owner_id),
        )
        if cursor.rowcount == 0:
            return None
        row = connection.execute(
            """
            SELECT id, owner_id, title, body, created_at, updated_at
              FROM comments WHERE id = ? AND owner_id = ?
            """,
            (comment_id, owner_id),
        ).fetchone()
    return dict(row)


def delete(owner_id: int, comment_id: int) -> bool:
    with session() as connection:
        cursor = connection.execute(
            "DELETE FROM comments WHERE id = ? AND owner_id = ?",
            (comment_id, owner_id),
        )
        return cursor.rowcount > 0
