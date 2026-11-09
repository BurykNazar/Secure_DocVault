"""Незмінна конфігурація застосунку.

Значення читаються один раз під час старту процесу. Якщо потрібно
змінити адресу, шлях або фактор хешування — це робиться через .env,
без правок коду.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from . import environment as env

ROOT = Path(__file__).resolve().parents[2]
env.load_env(ROOT)


@dataclass(frozen=True, slots=True)
class Settings:
    host: str
    port: int
    debug: bool
    data_dir: Path
    database: Path
    client: Path
    hash_rounds: int
    jwt_secret: str
    file_key: str
    cookie_secure: bool
    cors_origins: tuple[str, ...]

    @classmethod
    def read(cls) -> "Settings":
        data = env.path("VAULT_DATA_DIR", ROOT / "var", ROOT)
        return cls(
            host=env.text("VAULT_HOST", "127.0.0.1"),
            port=env.number("VAULT_PORT", 8000),
            debug=env.flag("VAULT_DEBUG", False),
            data_dir=data,
            database=env.path("VAULT_DB", data / "vault.sqlite3", ROOT),
            client=ROOT / "frontend",
            # bcrypt приймає 4..31; тримаємо здоровий діапазон.
            hash_rounds=max(4, min(env.number("VAULT_HASH_ROUNDS", 12), 15)),
            # 64 hex-символи = 256 біт. У робочому середовищі задається
            # через .env; значення нижче — лише для локального запуску.
            jwt_secret=env.text(
                "VAULT_JWT_SECRET",
                "7d3f9a2c5e8b1d4f6a9c3e7b0d5f8a2c"
                "4e6b9d1f3a5c7e0b2d4f6a8c1e3b5d7f",
            ),
            file_key=env.text(
                "VAULT_FILE_KEY",
                "a1b2c3d4e5f60718293a4b5c6d7e8f90"
                "112233445566778899aabbccddeeff00",
            ),
            # Secure-cookie працює за HTTPS (або на localhost). Для
            # звичайного HTTP-демо можна вимкнути через .env.
            cookie_secure=env.flag("VAULT_COOKIE_SECURE", True),
            cors_origins=tuple(
                item.strip()
                for item in env.text(
                    "VAULT_CORS_ORIGINS",
                    "http://127.0.0.1:8000,http://localhost:8000",
                ).split(",")
                if item.strip()
            ),
        )


settings = Settings.read()

__all__ = ["Settings", "settings", "ROOT"]
