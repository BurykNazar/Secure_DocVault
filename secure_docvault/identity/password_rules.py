"""Вимоги до пароля.

Усі зауваження збираються одразу: форма має показати людині повний
перелік того, що потрібно виправити, а не по одній причині за спробу.
"""

from __future__ import annotations

import re

MIN_LENGTH = 8
MAX_BYTES = 72
SPECIALS = set("!@#$%^&*()_+-=[]{};:'\",.<>/?\\|`~")
BLOCKLIST = {
    "password1!",
    "qwerty123!",
    "admin123!",
    "welcome1!",
    "letmein1!",
    "qwerty123",
    "password123",
}


def problems(secret: str, *, username: str = "", email: str = "") -> list[str]:
    if not secret:
        return ["Вкажіть пароль"]

    found: list[str] = []
    if len(secret) < MIN_LENGTH:
        found.append("Щонайменше 8 символів")
    if len(secret.encode("utf-8")) > MAX_BYTES:
        found.append("Не більше 72 байтів")
    if not re.search(r"[A-Z]", secret):
        found.append("Додайте велику літеру")
    if not re.search(r"[a-z]", secret):
        found.append("Додайте малу літеру")
    if not re.search(r"\d", secret):
        found.append("Додайте цифру")
    if not (set(secret) & SPECIALS):
        found.append("Додайте спеціальний символ")
    if re.search(r"\s", secret):
        found.append("Без пробілів")
    if len(username) >= 3 and username.lower() in secret.lower():
        found.append("Не повторюйте ім'я користувача")
    local = email.split("@", 1)[0] if email else ""
    if len(local) >= 3 and local.lower() in secret.lower():
        found.append("Не повторюйте частину пошти")
    if secret.lower() in BLOCKLIST:
        found.append("Цей пароль надто поширений")
    return found
