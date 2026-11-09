"""Псує один байт збереженого ЕЦП для перевірки на сайті.

    python tools\\tamper_signature.py Bur3
    python tools\\tamper_signature.py --restore

Змінюється підпис у var/vault.sqlite3, а не шифроконтейнер:
AES-GCM перевіряється раніше, тому байт у .enc дасть integrity_failed.
"""

from __future__ import annotations

import base64
import json
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from secure_docvault.settings import settings  # noqa: E402

BACKUP = settings.data_dir / "signature_backup.json"


def connect() -> sqlite3.Connection:
    connection = sqlite3.connect(settings.database)
    connection.row_factory = sqlite3.Row
    return connection


def restore() -> int:
    if not BACKUP.is_file():
        print("Резервної копії підпису немає.")
        return 1
    data = json.loads(BACKUP.read_text(encoding="utf-8"))
    with connect() as connection:
        connection.execute(
            "UPDATE document_signatures SET signature_b64 = ? "
            "WHERE document_id = ?",
            (data["signature_b64"], data["document_id"]),
        )
    BACKUP.unlink()
    print(f"Підпис відновлено для {data['original_filename']}.")
    return 0


def main() -> int:
    if "--restore" in sys.argv:
        return restore()
    if BACKUP.exists():
        print("Спочатку відновіть підпис:")
        print("python tools\\tamper_signature.py --restore")
        return 1

    username = next((arg for arg in sys.argv[1:] if not arg.startswith("-")), None)
    query = """
        SELECT d.original_filename, s.document_id, s.signature_b64,
               u.username AS signer
          FROM document_signatures s
          JOIN documents d ON d.id = s.document_id
          JOIN users u ON u.id = s.signer_id
    """
    params: tuple[str, ...] = ()
    if username:
        query += " WHERE u.username = ?"
        params = (username,)
    query += " ORDER BY s.signed_at DESC, s.rowid DESC LIMIT 1"

    with connect() as connection:
        row = connection.execute(query, params).fetchone()
        if not row:
            print("Підписів не знайдено.")
            return 1

        raw = bytearray(base64.b64decode(row["signature_b64"]))
        raw[0] ^= 0xFF
        backup = {
            "document_id": row["document_id"],
            "original_filename": row["original_filename"],
            "signature_b64": row["signature_b64"],
        }
        BACKUP.write_text(json.dumps(backup), encoding="utf-8")
        connection.execute(
            "UPDATE document_signatures SET signature_b64 = ? "
            "WHERE document_id = ?",
            (base64.b64encode(raw).decode("ascii"), row["document_id"]),
        )

    print("Змінено 1 байт збереженого ЕЦП.")
    print(f"Документ : {row['original_filename']}")
    print(f"Підписант: {row['signer']}")
    print("Натисніть «Скачати» на сайті — очікується 409 signature_invalid.")
    print("Відновлення: python tools\\tamper_signature.py --restore")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
