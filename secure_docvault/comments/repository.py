"""SQL для коментарів до документів."""

from __future__ import annotations

from ..persistence.engine import session


def list_for(document_id: str, author_id: int) -> list[dict]:
    with session() as connection:
        rows = connection.execute(
            """
            SELECT id, title, body, created_at, updated_at
              FROM document_comments
             WHERE document_id = ? AND author_id = ? ORDER BY id DESC
            """,
            (document_id, author_id),
        ).fetchall()
    return [dict(row) for row in rows]


def create(document_id: str, author_id: int, title: str, body: str) -> dict:
    with session() as connection:
        cursor = connection.execute(
            """
            INSERT INTO document_comments (document_id, author_id, title, body)
            VALUES (?, ?, ?, ?)
            """,
            (document_id, author_id, title, body),
        )
        row = connection.execute(
            """
            SELECT id, title, body, created_at, updated_at
              FROM document_comments WHERE id = ?
            """,
            (int(cursor.lastrowid),),
        ).fetchone()
    return dict(row)


def update(
    document_id: str, author_id: int, comment_id: int, title: str, body: str
) -> dict | None:
    with session() as connection:
        cursor = connection.execute(
            """
            UPDATE document_comments
               SET title = ?, body = ?, updated_at = CURRENT_TIMESTAMP
             WHERE id = ? AND document_id = ? AND author_id = ?
            """,
            (title, body, comment_id, document_id, author_id),
        )
        if cursor.rowcount == 0:
            return None
        row = connection.execute(
            """
            SELECT id, title, body, created_at, updated_at
              FROM document_comments
             WHERE id = ? AND document_id = ? AND author_id = ?
            """,
            (comment_id, document_id, author_id),
        ).fetchone()
    return dict(row)


def delete(document_id: str, author_id: int, comment_id: int) -> bool:
    with session() as connection:
        cursor = connection.execute(
            """
            DELETE FROM document_comments
             WHERE id = ? AND document_id = ? AND author_id = ?
            """,
            (comment_id, document_id, author_id),
        )
        return cursor.rowcount > 0
