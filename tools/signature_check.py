"""Демонстрація ЕЦП RSA-PSS: підпис, верифікація та підробка.

Запуск із кореня проєкту::

    python tools/signature_check.py

Скрипт не звертається до БД: він показує математику підпису, експорт
PEM і те, що зміна одного слова робить підпис недійсним.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from secure_docvault.signing import keys  # noqa: E402


def main() -> int:
    original = b"OFFICIAL STATEMENT: APPROVED BY CHIEF SECURITY OFFICER"
    print("=" * 58)
    print("ТЕСТУВАННЯ ЕЦП RSA-PSS / SHA-256")
    print("=" * 58)
    print("1. Документ:", original.decode())

    private_key, public_key = keys.generate_keypair()
    print("2. Ключову пару RSA-2048 згенеровано")
    print(f"   Відбиток відкритого ключа: {keys.fingerprint(public_key)}")

    signature = keys.sign_content(original, private_key)
    print(f"3. Підпис створено, довжина: {len(signature)} байт")

    if not keys.verify_content(original, signature, public_key):
        print("   ПОМИЛКА: штатний підпис не пройшов перевірку")
        return 1
    print("4. Штатний підпис успішно верифіковано")

    tampered = original.replace(b"APPROVED", b"REJECTED")
    valid = keys.verify_content(tampered, signature, public_key)
    print("5. Перевірка підробленого документа...")
    if valid:
        print("   ПОМИЛКА БЕЗПЕКИ: підпис прийняв змінений документ!")
        return 1
    print("   --> УСПІХ: підпис відхилив змінений документ!")

    public_pem = keys.serialize_public_key(public_key)
    private_pem = keys.serialize_private_key(private_key, "Aa1!aaaa")
    assert "BEGIN PUBLIC KEY" in public_pem
    assert "BEGIN ENCRYPTED PRIVATE KEY" in private_pem
    assert keys.load_public_key(public_pem).key_size == 2048
    assert keys.load_private_key(private_pem, "Aa1!aaaa").key_size == 2048
    print("6. PEM: X.509 public + PKCS#8 private (пароль) — OK")
    print("=" * 58)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
