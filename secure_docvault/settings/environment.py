"""Читання налаштувань зі змінних оточення.

Один модуль відповідає лише за перетворення «сирого» рядка з оточення
на потрібний тип. Жодних бізнесових рішень тут немає.
"""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv


def load_env(root: Path) -> None:
    """Підхоплює .env із кореня проєкту, якщо він існує."""
    load_dotenv(root / ".env")


def text(name: str, fallback: str) -> str:
    raw = os.getenv(name)
    return raw.strip() if raw and raw.strip() else fallback


def number(name: str, fallback: int) -> int:
    raw = os.getenv(name, "").strip()
    try:
        return int(raw)
    except ValueError:
        return fallback


def flag(name: str, fallback: bool) -> bool:
    raw = os.getenv(name)
    if raw is None or not raw.strip():
        return fallback
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def path(name: str, fallback: Path, root: Path) -> Path:
    """Відносні шляхи з оточення рахує від кореня проєкту."""
    raw = os.getenv(name)
    if raw is None or not raw.strip():
        return fallback
    candidate = Path(raw.strip()).expanduser()
    return candidate.resolve() if candidate.is_absolute() else (root / candidate).resolve()
