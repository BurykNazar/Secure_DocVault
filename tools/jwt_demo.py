"""Покрокова демонстрація JWT для протоколу ЛР №2.

Сервер має бути запущений, а залежності — встановлені. Між кроками
скрипт чекає Enter, тому кожен екран зручно сфотографувати.

    python tools/jwt_demo.py
"""

from __future__ import annotations

import argparse
import json
import urllib.error
import urllib.request

import jwt

LINE = "=" * 70


def call(method: str, url: str, payload: dict | None = None, token: str | None = None):
    headers = {"Accept": "application/json"}
    data = None
    if payload is not None:
        headers["Content-Type"] = "application/json"
        data = json.dumps(payload).encode("utf-8")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(request, timeout=5) as response:
            return response.status, json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        return error.code, json.loads(error.read().decode("utf-8"))


def show(status: int, body: dict, expected: int | None = None) -> None:
    mark = "" if expected is None else ("  [OK]" if status == expected else "  [?!]")
    print(f"HTTP {status}{mark}")
    print(json.dumps(body, indent=2, ensure_ascii=False))


def step(title: str, wait: bool) -> None:
    print(f"\n{LINE}\n{title}\n{LINE}")
    if wait:
        input("\nEnter — далі…")


def main() -> int:
    parser = argparse.ArgumentParser(description="Демонстрація JWT для звіту")
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    parser.add_argument("--username", default="nazar_buryk")
    parser.add_argument("--password", default="Dossier2026!")
    parser.add_argument("--no-wait", action="store_true", help="не чекати Enter")
    args = parser.parse_args()
    base, wait = args.base_url, not args.no_wait

    step("1. POST /api/v1/accounts/login — отримання пари токенів", False)
    status, body = call(
        "POST",
        f"{base}/api/v1/accounts/login",
        {"username": args.username, "password": args.password},
    )
    show(status, body, 200)
    if status != 200:
        print("\nПеревірте ім'я/пароль або зареєструйте користувача у вебклієнті.")
        return 1
    access, refresh = body["access_token"], body["refresh_token"]
    step("2. GET /api/v1/user/profile — валідний Bearer-токен", wait)
    show(*call("GET", f"{base}/api/v1/user/profile", token=access), 200)

    step("3. GET /api/v1/user/profile — без заголовка Authorization", wait)
    show(*call("GET", f"{base}/api/v1/user/profile"), 401)

    step("4. Підміна ролі: у payload записано admin, підпис чужий", wait)
    claims = jwt.decode(access, options={"verify_signature": False})
    claims["role"] = "admin"
    forged = jwt.encode(claims, "attacker-secret-key-32-bytes-long!!", algorithm="HS256")
    print("Змінений payload:")
    print(json.dumps(claims, indent=2, ensure_ascii=False))
    print("\nВідповідь сервера:")
    show(*call("GET", f"{base}/api/v1/user/profile", token=forged), 401)

    step("5. POST /api/v1/auth/refresh — ротація пари", wait)
    status, body = call(
        "POST", f"{base}/api/v1/auth/refresh", {"refresh_token": refresh}
    )
    show(status, body, 200)
    if status == 200:
        print(f"\nНовий access  відрізняється: {body['access_token'] != access}")
        print(f"Новий refresh відрізняється: {body['refresh_token'] != refresh}")
    print("\nПовторне використання старого refresh-токена:")
    show(*call("POST", f"{base}/api/v1/auth/refresh", {"refresh_token": refresh}), 401)

    print(f"\n{LINE}\nГотово. Можна робити скриншоти.\n{LINE}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
