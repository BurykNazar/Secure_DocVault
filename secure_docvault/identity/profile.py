"""Публічне представлення облікового запису.

Назовні віддаємо лише те, що потрібно інтерфейсу. Хеш, сіль,
лічильники та службові поля ніколи не покидають сервер.
"""

from __future__ import annotations


def public(account: dict) -> dict:
    return {
        "id": account["id"],
        "username": account["username"],
        "email": account["email"],
        "role": account["role"],
        "created_at": account["created_at"],
    }
