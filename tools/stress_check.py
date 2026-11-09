"""Стрес-перевірка Rate Limiter та WAF.

Сервер має бути запущений::

    python manage.py
    python tools/stress_check.py

Після тесту WAF поточна IP-адреса потрапляє в Greylist на 5 хвилин.
Щоб одразу продовжити роботу, перезапустіть сервер.
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request


def send(method: str, url: str, payload: dict | None = None):
    data = None
    headers = {"Accept": "application/json"}
    if payload is not None:
        headers["Content-Type"] = "application/json"
        data = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(request, timeout=5) as response:
            body = json.loads(response.read().decode("utf-8"))
            return response.status, body, response.headers
    except urllib.error.HTTPError as error:
        raw = error.read().decode("utf-8", errors="replace")
        try:
            body = json.loads(raw)
        except json.JSONDecodeError:
            body = {"raw": raw}
        return error.code, body, error.headers


def main() -> int:
    parser = argparse.ArgumentParser(description="Rate limit і WAF")
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    parser.add_argument("--username", default="nazar_buryk")
    parser.add_argument("--password", default="Dossier2026!")
    args = parser.parse_args()
    base = args.base_url

    print("1. Rate Limiter: 10 спроб входу поспіль\n")
    login = f"{base}/api/v1/accounts/login"
    for number in range(1, 11):
        status, body, headers = send(
            "POST",
            login,
            {"username": args.username, "password": args.password},
        )
        retry = headers.get("Retry-After", "-")
        code = body.get("error", {}).get("code", "")
        print(f"  #{number:02d}  HTTP {status}  Retry-After: {retry}  {code}")

    print("\n2. WAF: Path Traversal\n")
    status, body, _ = send(
        "GET", f"{base}/api/v1/user/profile?file=../../etc/passwd"
    )
    print(f"  HTTP {status}  {body.get('error', {}).get('message', '')}")

    print("\n3. Greylist: звичайний запит після атаки\n")
    status, body, _ = send("GET", f"{base}/api/v1/user/profile")
    print(f"  HTTP {status}  {body.get('error', {}).get('code', '')}")

    print("\nГотово. IP у Greylist на 5 хв — перезапустіть сервер, щоб скинути.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
