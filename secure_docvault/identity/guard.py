"""Перевірка заголовка Authorization для захищених маршрутів."""

from __future__ import annotations

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from ..transport.errors import TokenRejected
from .tokens import decode

_bearer = HTTPBearer(auto_error=False)


def current_claims(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
) -> dict:
    if credentials is None:
        raise TokenRejected("Відсутній заголовок Authorization: Bearer <token>")
    return decode(credentials.credentials, "access")
