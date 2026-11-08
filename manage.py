"""Запуск сервера: ``python manage.py``."""

from __future__ import annotations

import uvicorn

from secure_docvault.settings import settings


def main() -> None:
    uvicorn.run(
        "secure_docvault.factory:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
    )


if __name__ == "__main__":
    main()
