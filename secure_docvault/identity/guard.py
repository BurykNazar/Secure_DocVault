"""Перевірка заголовка Authorization або HttpOnly cookie."""

from __future__ import annotations

from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from ..transport.cookies import ACCESS_COOKIE
from ..transport.errors import TokenRejected
from .tokens import decode

_bearer = HTTPBearer(auto_error=False)


def current_claims(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
) -> dict:
    # Явний Bearer має пріоритет; інакше вебклієнт автентифікується
    # HttpOnly-cookie, яку браузер надсилає автоматично.
    token = credentials.credentials if credentials else request.cookies.get(ACCESS_COOKIE)

    if not token:
        raise TokenRejected("Відсутній заголовок Authorization: Bearer <token>")
    return decode(token, "access")
