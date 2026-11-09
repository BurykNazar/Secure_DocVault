"""Демонстрація стійкості входу до SQL-ін'єкцій.

Сервер має бути запущений::

    python manage.py
    python tools/injection_check.py
"""

from __future__ import annotations

import argparse
import json
import sqlite3
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from secure_docvault.settings import settings  # noqa: E402

PAYLOADS = [
    ("класичний обхід", "' OR '1'='1"),
    ("коментар після імені", "admin' --"),
    ("UNION SELECT", "' UNION SELECT id, username, email, password_hash, salt FROM users --"),
    ("спроба DROP TABLE", "'; DROP TABLE users; --"),
    ("подвійні лапки", '" OR ""="'),
]


def post(url: str, payload: dict) -> tuple[int, dict]:
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json", "Accept": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=5) as response:
            return response.status, json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        raw = error.read().decode("utf-8", errors="replace")
        try:
            return error.code, json.loads(raw)
        except json.JSONDecodeError:
            return error.code, {"raw": raw}


def main() -> int:
    parser = argparse.ArgumentParser(description="Перевірка захисту від SQL-ін'єкцій")
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    args = parser.parse_args()

    login = f"{args.base_url}/api/v1/accounts/login"
    register = f"{args.base_url}/api/v1/accounts/register"
    try:
        urllib.request.urlopen(args.base_url, timeout=5).close()
    except (urllib.error.URLError, TimeoutError):
        print(f"Сервер недоступний: {args.base_url}. Запустіть `python manage.py`.")
        return 1

    print("1. Вхід із payload'ами SQL-ін'єкції\n")
    failures = 0
    for label, payload in PAYLOADS:
        status, body = post(login, {"username": payload, "password": "WrongPass1!"})
        verdict = "ЗАХИЩЕНО" if status in (401, 403) else "ПЕРЕВІРИТИ"
        failures += status not in (401, 403)
        print(f"  [{verdict}] HTTP {status} — {label}")
        print(f"             payload: {payload}")
        print(f"             відповідь: {body.get('error', {}).get('message', '')}\n")

    print("2. Реєстрація з SQL-синтаксисом в імені\n")
    status, body = post(
        register,
        {"username": "admin' OR '1'='1", "email": "attacker@example.com", "password": "SecurePass1!"},
    )
    verdict = "ЗАХИЩЕНО" if status in (400, 403) else "ПЕРЕВІРИТИ"
    failures += status not in (400, 403)
    fields = json.dumps(body.get("error", {}).get("fields", {}), ensure_ascii=False)
    print(f"  [{verdict}] HTTP {status}\n             поля: {fields}\n")

    print("3. Цілісність бази після атак\n")
    connection = sqlite3.connect(settings.database)
    try:
        total = connection.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    finally:
        connection.close()
    print(f"  Таблиця users доступна, записів: {total}")

    if failures:
        print(f"\nПроблем: {failures}. Перевірте серверну логіку.")
        return 1

    print("\nУсі спроби відхилено: параметризовані запити працюють.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
