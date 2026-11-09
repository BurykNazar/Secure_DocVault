"""Останній збережений ЕЦП для протоколу ЛР №6.

Запуск із кореня проєкту::

    python tools/signature_report.py
"""

from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from secure_docvault.settings import settings  # noqa: E402


def main() -> int:
    if not settings.database.is_file():
        print("Базу ще не створено — запустіть сервер і завантажте документ.")
        return 1

    requested_user = sys.argv[1].strip() if len(sys.argv) > 1 else None
    query = """
        SELECT d.original_filename, s.document_id, u.username AS signer,
               s.algorithm, s.signature_b64,
               s.public_key_fingerprint, s.signed_at
          FROM document_signatures s
          JOIN documents d ON d.id = s.document_id
          JOIN users u ON u.id = s.signer_id
    """
    params: tuple[str, ...] = ()
    if requested_user:
        query += " WHERE u.username = ?"
        params = (requested_user,)
    query += " ORDER BY s.signed_at DESC, s.rowid DESC LIMIT 1"

    connection = sqlite3.connect(settings.database)
    connection.row_factory = sqlite3.Row
    row = connection.execute(query, params).fetchone()
    connection.close()

    if not row:
        if requested_user:
            print(f"У користувача {requested_user} підписів немає.")
        else:
            print("Підписів у базі немає — завантажте документ.")
        return 1

    signature = row["signature_b64"]
    print("Останній ЕЦП у базі даних")
    print(f"Документ    : {row['original_filename']}")
    print(f"Document ID : {row['document_id']}")
    print(f"Підписант   : {row['signer']}")
    print(f"Алгоритм    : {row['algorithm']}")
    print(f"Підпис      : {signature[:24]}… ({len(signature)} символів)")
    print(f"Відбиток    : {row['public_key_fingerprint']}")
    print(f"Створено    : {row['signed_at']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
