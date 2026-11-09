"""Перевірка ЕЦП через API для протоколу ЛР №6.

Сервер має бути запущений::

    python tools/api_signature_check.py
    python tools/api_signature_check.py lab6.txt
"""

from __future__ import annotations

import getpass
import json
import sys
import urllib.error
import urllib.request

BASE = "http://127.0.0.1:8000"


def request(method: str, path: str, payload: dict | None = None, token: str | None = None):
    headers = {"Accept": "application/json"}
    data = None
    if payload is not None:
        headers["Content-Type"] = "application/json"
        data = json.dumps(payload).encode("utf-8")
    if token:
        headers["Authorization"] = f"Bearer {token}"

    req = urllib.request.Request(BASE + path, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            return response.status, dict(response.headers), response.read()
    except urllib.error.HTTPError as error:
        return error.code, dict(error.headers), error.read()
    except urllib.error.URLError as error:
        raise SystemExit(f"Сервер недоступний: {error.reason}") from error


def header(headers: dict[str, str], name: str) -> str:
    return next(
        (value for key, value in headers.items() if key.lower() == name.lower()),
        "—",
    )


def main() -> int:
    username = input("Логін: ").strip()
    password = getpass.getpass("Пароль: ")

    status, _, body = request("POST", "/api/v1/accounts/login",
                              {"username": username, "password": password})
    print(f"POST /api/v1/accounts/login -> {status}")
    if status != 200:
        print(body.decode("utf-8", "replace")[:300])
        return 1
    token = json.loads(body)["access_token"]

    status, _, body = request("GET", "/api/v1/documents", token=token)
    documents = json.loads(body).get("documents", []) if status == 200 else []
    print(f"GET  /api/v1/documents -> {status} (документів: {len(documents)})")

    wanted = sys.argv[1].strip() if len(sys.argv) > 1 else None
    signed = [
        item
        for item in documents
        if item.get("signature", {}).get("status") in {"signed", "verified"}
    ]
    if wanted:
        signed = [item for item in signed if item["original_filename"] == wanted]

    if not signed:
        print("Підписаних документів не знайдено.")
        return 1

    document = signed[0]
    status, headers, body = request("GET",
        f"/api/v1/documents/{document['id']}/download", token=token)
    print(
        f"GET  /api/v1/documents/{document['id']}/download -> {status}"
    )
    if status != 200:
        print(body.decode("utf-8", "replace")[:300])
        return 1

    print()
    print(f"Документ            : {document['original_filename']}")
    print(f"Розмір              : {len(body)} байт")
    for name in (
        "X-Signature-Status",
        "X-Signature-Algorithm",
        "X-Signer",
        "X-Signature-Fingerprint",
        "X-Signed-At",
    ):
        print(f"{name:24}: {header(headers, name)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
