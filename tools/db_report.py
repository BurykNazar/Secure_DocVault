"""Показ вмісту таблиці users для протоколу тестування.

Запуск із кореня проєкту після хоча б однієї реєстрації::

    python tools/db_report.py
"""

from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from secure_docvault.settings import settings  # noqa: E402


def main() -> int:
    print(f"База даних: {settings.database}")
    if not settings.database.is_file():
        print("Базу ще не створено — запустіть сервер і зареєструйте користувача.")
        return 1

    connection = sqlite3.connect(settings.database)
    connection.row_factory = sqlite3.Row
    rows = connection.execute(
        """
        SELECT id, username, email, password_hash, salt, role,
               created_at, is_active, failed_attempts, locked_until
          FROM users ORDER BY id
        """
    ).fetchall()
    connection.close()

    if not rows:
        print("Таблиця users порожня.")
        return 0

    print(f"Записів: {len(rows)}\n")
    for row in rows:
        print(f"#{row['id']}  {row['username']}")
        print(f"    email           : {row['email']}")
        print(f"    password_hash   : {row['password_hash']}")
        print(f"    salt            : {row['salt']}")
        print(f"    role            : {row['role']}")
        print(f"    created_at      : {row['created_at']}")
        print(f"    is_active       : {row['is_active']}")
        print(f"    failed_attempts : {row['failed_attempts']}")
        print(f"    locked_until    : {row['locked_until'] or '—'}")
        print()

    print("Відкритого пароля немає — лише bcrypt-хеш із сіллю.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
