"""SQL для ключів і підписів ЕЦП."""

from __future__ import annotations

from ..persistence.engine import one, session


def get_key(user_id: int) -> dict | None:
    with session() as connection:
        row = connection.execute(
            "SELECT * FROM user_signing_keys WHERE user_id = ?",
            (user_id,),
        ).fetchone()
    return dict(row) if row else None


def save_key(
    user_id: int,
    algorithm: str,
    public_key_pem: str,
    private_key_encrypted: str,
    key_fingerprint: str,
) -> bool:
    with session() as connection:
        cursor = connection.execute(
            """
            INSERT INTO user_signing_keys (
                user_id, algorithm, public_key_pem,
                private_key_encrypted, key_fingerprint
            ) VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(user_id) DO NOTHING
            """,
            (
                user_id,
                algorithm,
                public_key_pem,
                private_key_encrypted,
                key_fingerprint,
            ),
        )
        return cursor.rowcount > 0


def get_signature(document_id: str) -> dict | None:
    with session() as connection:
        row = connection.execute(
            "SELECT * FROM document_signatures WHERE document_id = ?",
            (document_id,),
        ).fetchone()
    return dict(row) if row else None


def save_signature(
    document_id: str,
    signer_id: int,
    algorithm: str,
    signature_b64: str,
    public_key_fingerprint: str,
) -> None:
    with session() as connection:
        connection.execute(
            """
            INSERT INTO document_signatures (
                document_id, signer_id, algorithm,
                signature_b64, public_key_fingerprint
            ) VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(document_id) DO UPDATE SET
                signer_id = excluded.signer_id,
                algorithm = excluded.algorithm,
                signature_b64 = excluded.signature_b64,
                public_key_fingerprint = excluded.public_key_fingerprint
            """,
            (
                document_id,
                signer_id,
                algorithm,
                signature_b64,
                public_key_fingerprint,
            ),
        )


def username(user_id: int) -> str | None:
    row = one("SELECT username FROM users WHERE id = ?", (user_id,))
    return row["username"] if row else None
