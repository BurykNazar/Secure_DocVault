"""Захисні cookie для вебклієнта."""

from __future__ import annotations

from fastapi import Response

from ..identity.tokens import ACCESS_MINUTES
from ..settings import settings

ACCESS_COOKIE = "vault_access"


def set_access_cookie(response: Response, token: str) -> None:
    """HttpOnly + Secure + SameSite=Strict.

    HttpOnly забороняє читання з JavaScript, SameSite=Strict не дає
    браузеру надсилати cookie в міжсайтових запитах (CSRF).
    """
    response.set_cookie(
        key=ACCESS_COOKIE,
        value=token,
        max_age=ACCESS_MINUTES * 60,
        path="/",
        httponly=True,
        secure=settings.cookie_secure,
        samesite="strict",
    )
