"""Вимоги до пароля.

Перелік відповідає методичним вказівкам: довжина, літери різного
регістру, цифра та спеціальний символ. Додатково враховано фізичне
обмеження bcrypt у 72 байти.
"""

from __future__ import annotations

import re

MIN_LENGTH = 8
MAX_BYTES = 72
SPECIALS = set("!@#$%^&*()_+-=[]{};:'\",.<>/?\\|`~")


def problems(secret: str) -> list[str]:
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
    return found
