"""bcrypt-перетворення паролів.

Сіль генерує сам bcrypt для кожного запису. Порівняння виконується
функцією checkpw, яка не «виходить достроково» на першому розбіжному
байті, тому час відповіді не залежить від правильності префікса пароля.
"""

from __future__ import annotations

import secrets
from functools import lru_cache

import bcrypt

from ..settings import settings

BYTE_LIMIT = 72


def seal(password: str) -> tuple[str, str]:
    """Повертає (хеш, сіль). Сіль — службова копія з початку хеша."""
    raw = password.encode("utf-8")
    if len(raw) > BYTE_LIMIT:
        raise ValueError("Пароль перевищує 72 байти")
    salt = bcrypt.gensalt(rounds=settings.hash_rounds)
    digest = bcrypt.hashpw(raw, salt)
    return digest.decode("ascii"), salt.decode("ascii")


def matches(password: str, digest: str) -> bool:
    raw = password.encode("utf-8")
    if len(raw) > BYTE_LIMIT:
        return False
    try:
        return bcrypt.checkpw(raw, digest.encode("ascii"))
    except (ValueError, TypeError):
        return False


@lru_cache(maxsize=1)
def _decoy() -> str:
    salt = bcrypt.gensalt(rounds=settings.hash_rounds)
    return bcrypt.hashpw(secrets.token_bytes(32), salt).decode("ascii")


def spend_comparison_time(password: str) -> None:
    """Холостий прогін, щоб «немає такого користувача» не відрізнялося
    за часом від «є користувач, але пароль невірний»."""
    raw = password.encode("utf-8")[:BYTE_LIMIT]
    try:
        bcrypt.checkpw(raw, _decoy().encode("ascii"))
    except (ValueError, TypeError):
        pass
