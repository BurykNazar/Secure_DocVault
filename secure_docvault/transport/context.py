"""Наскрізні позначки запиту.

Ідентифікатор запиту допомагає зіставити відповідь із рядком журналу.
Відповіді API не кешуються браузером.
"""

from __future__ import annotations

import uuid

from fastapi import Request


async def stamp(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID") or uuid.uuid4().hex
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    if request.url.path.startswith("/api/"):
        response.headers["Cache-Control"] = "no-store"
    return response
