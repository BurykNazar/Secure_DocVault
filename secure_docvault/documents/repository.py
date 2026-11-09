"""SQL для документів."""

from __future__ import annotations

from ..persistence.engine import session


def save(
    doc_id: str,
    owner_id: int,
    original_filename: str,
    stored_filename: str,
    content_type: str,
    size_bytes: int,
    encrypted_size: int,
    sha256: str,
) -> None:
    with session() as connection:
        connection.execute(
            """
            INSERT INTO documents (
                id, owner_id, original_filename, stored_filename,
                content_type, size_bytes, encrypted_size, sha256
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                doc_id,
                owner_id,
                original_filename,
                stored_filename,
                content_type,
                size_bytes,
                encrypted_size,
                sha256,
            ),
        )


def list_for(owner_id: int) -> list[dict]:
    with session() as connection:
        rows = connection.execute(
            """
            SELECT id, original_filename, content_type, size_bytes,
                   encrypted_size, created_at
              FROM documents WHERE owner_id = ? ORDER BY created_at DESC
            """,
            (owner_id,),
        ).fetchall()
    return [dict(row) for row in rows]


def get_for(owner_id: int, doc_id: str) -> dict | None:
    with session() as connection:
        row = connection.execute(
            """
            SELECT id, owner_id, original_filename, stored_filename,
                   content_type, size_bytes, sha256, created_at
              FROM documents WHERE id = ? AND owner_id = ?
            """,
            (doc_id, owner_id),
        ).fetchone()
    return dict(row) if row else None


def delete(owner_id: int, doc_id: str) -> bool:
    with session() as connection:
        cursor = connection.execute(
            "DELETE FROM documents WHERE id = ? AND owner_id = ?",
            (doc_id, owner_id),
        )
        return cursor.rowcount > 0
