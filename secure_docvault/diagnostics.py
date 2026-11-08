"""Журнали застосунку та подій доступу.

application.log — технічний перебіг роботи сервера.
access.log      — події безпеки у форматі JSON Lines (вхід, відмови,
                  блокування). Саме цей файл використовується під час
                  перевірки протоколу тестування.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from logging.handlers import RotatingFileHandler

from .settings import settings

_ready = False


def _rotation(file_name: str, formatter: logging.Formatter) -> RotatingFileHandler:
    handler = RotatingFileHandler(
        settings.logs / file_name,
        maxBytes=4 * 1024 * 1024,
        backupCount=4,
        encoding="utf-8",
    )
    handler.setFormatter(formatter)
    return handler


def configure() -> None:
    global _ready
    if _ready:
        return
    _ready = True

    settings.logs.mkdir(parents=True, exist_ok=True)
    layout = logging.Formatter("%(asctime)s %(levelname)-7s %(name)s — %(message)s")

    console = logging.StreamHandler()
    console.setFormatter(layout)

    app = logging.getLogger("vault")
    app.setLevel(logging.DEBUG if settings.debug else logging.INFO)
    app.propagate = False
    app.addHandler(console)
    app.addHandler(_rotation("application.log", layout))

    access = logging.getLogger("vault.access")
    access.setLevel(logging.INFO)
    access.propagate = False
    access.addHandler(_rotation("access.log", logging.Formatter("%(message)s")))


def audit(event: str, **details: object) -> None:
    record = {
        "at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "event": event,
        **details,
    }
    logging.getLogger("vault.access").info(
        json.dumps(record, ensure_ascii=False, default=str)
    )
