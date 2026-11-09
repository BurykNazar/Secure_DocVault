"""Файлове сховище шифроконтейнерів."""

from __future__ import annotations

from pathlib import Path

from ..security.vault import associated, decrypt, encrypt
from ..settings import settings
from ..transport.errors import MissingResource

MAX_BYTES = 10 * 1024 * 1024
CHUNK = 1024 * 1024


def directory() -> Path:
    path = settings.data_dir / "uploads"
    path.mkdir(parents=True, exist_ok=True)
    return path


def write(doc_id: str, owner_id: int, data: bytes) -> tuple[str, int]:
    blob = encrypt(data, associated(doc_id, owner_id))
    stored = f"{doc_id}.enc"
    (directory() / stored).write_bytes(blob)
    return stored, len(blob)


def read(doc_id: str, owner_id: int, stored: str) -> bytes:
    path = directory() / Path(stored).name
    if not path.is_file():
        raise MissingResource("Зашифрований файл відсутній на диску")
    return decrypt(path.read_bytes(), associated(doc_id, owner_id))


def remove(stored: str) -> None:
    (directory() / Path(stored).name).unlink(missing_ok=True)
