"""Демонстрація AES-256-GCM і виявлення підміни файлу.

Запуск із кореня проєкту::

    python tools/integrity_check.py

Скрипт бере останній документ із БД, показує IV/Tag/hex контейнера,
розшифровує його, змінює один байт у файлі **на диску**, ловить
InvalidTag і відновлює початковий вміст.
"""

from __future__ import annotations

import sys
from pathlib import Path

from cryptography.exceptions import InvalidTag

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from secure_docvault.persistence import one  # noqa: E402
from secure_docvault.security.vault import associated, decrypt, encrypt  # noqa: E402
from secure_docvault.settings import settings  # noqa: E402


def _hex(blob: bytes, limit: int = 48) -> str:
    return " ".join(f"{byte:02x}" for byte in blob[:limit])


def main() -> int:
    row = one(
        """
        SELECT id, owner_id, stored_filename
          FROM documents ORDER BY created_at DESC LIMIT 1
        """
    )

    path = None
    if row:
        path = settings.data_dir / "uploads" / row["stored_filename"]
        if not path.is_file():
            print("Файл документа відсутній на диску.")
            return 1
        original = path.read_bytes()
        blob = original
        aad = associated(row["id"], row["owner_id"])
        plaintext = decrypt(blob, aad)
        print(f"Джерело: зашифрований файл {path.name}")
    else:
        plaintext = b"CONFIDENTIAL FINANCIAL REPORT - SECURE DOCVAULT 2026"
        aad = associated("demo-document", 1)
        blob = encrypt(plaintext, aad)
        print("Джерело: демонстраційний контейнер (документів у БД немає)")

    print(f"Розмір контейнера: {len(blob)} байт")
    print(f"IV (12 байт): {blob[:12].hex()}")
    print(f"Tag (16 байт): {blob[12:28].hex()}")
    print(f"Hex (перші 48 байт): {_hex(blob)}")
    print(f"Відкритий текст у контейнері: {plaintext[:20] in blob}")
    print(f"Штатне розшифрування: {decrypt(blob, aad) == plaintext}")

    corrupted = bytearray(blob)
    print(f"\nБайт 20 до зміни: {corrupted[20]:02x}")
    corrupted[20] ^= 0xFF
    print(f"Байт 20 після зміни: {corrupted[20]:02x}")

    if path:
        path.write_bytes(bytes(corrupted))
        changed = path.read_bytes()
        print(f"Змінено 1 байт у файлі на диску: uploads/{path.name}")
    else:
        changed = bytes(corrupted)
        print("Змінено 1 байт у контейнері в пам'яті")

    result = 0
    try:
        decrypt(changed, aad)
    except InvalidTag as error:
        print(f"--> УСПІХ: {type(error).__name__} — AES-GCM заблокував файл.")
    else:
        print("ПОМИЛКА БЕЗПЕКИ: підробка пройшла перевірку!")
        result = 1
    finally:
        if path:
            path.write_bytes(original)
            print("Файл на диску відновлено.")

    return result


if __name__ == "__main__":
    raise SystemExit(main())
