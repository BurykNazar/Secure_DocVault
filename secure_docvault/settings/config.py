"""Незмінна конфігурація застосунку.

Значення читаються один раз під час старту процесу. Якщо потрібно
змінити адресу, шлях або ліміти — це робиться через .env, без правок
коду.
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
    logs: Path
    client: Path
    hash_rounds: int
    max_failures: int
    lock_minutes: int

    @classmethod
    def read(cls) -> "Settings":
        data = env.path("VAULT_DATA_DIR", ROOT / "var", ROOT)
        return cls(
            host=env.text("VAULT_HOST", "127.0.0.1"),
            port=env.number("VAULT_PORT", 8000),
            debug=env.flag("VAULT_DEBUG", False),
            data_dir=data,
            database=env.path("VAULT_DB", data / "vault.sqlite3", ROOT),
            logs=env.path("VAULT_LOG_DIR", data / "logs", ROOT),
            client=ROOT / "frontend",
            # bcrypt приймає 4..31; тримаємо здоровий діапазон.
            hash_rounds=max(4, min(env.number("VAULT_HASH_ROUNDS", 12), 15)),
            max_failures=max(1, env.number("VAULT_MAX_FAILURES", 5)),
            lock_minutes=max(1, env.number("VAULT_LOCK_MINUTES", 15)),
        )


settings = Settings.read()

__all__ = ["Settings", "settings", "ROOT"]
