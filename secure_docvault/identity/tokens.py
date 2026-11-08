"""Випуск, перевірка та відкликання JWT.

Підпис — HMAC-SHA256 (HS256), ключ не коротший за 256 біт. Access-
токен живе 15 хвилин, refresh — 7 діб. Використані refresh-токени
потрапляють до списку відкликаних: повторне використання трактується
як replay-атака.
"""

from __future__ import annotations

import datetime
import uuid

import jwt

from ..settings import settings
from ..transport.errors import ReplayDetected, TokenRejected

ALGORITHM = "HS256"
ACCESS_MINUTES = 15
REFRESH_DAYS = 7

if len(settings.jwt_secret) < 32:
    raise RuntimeError("VAULT_JWT_SECRET має містити щонайменше 32 символи")

_REVOKED: set[str] = set()


def _now() -> datetime.datetime:
    return datetime.datetime.now(datetime.timezone.utc)


def _encode(claims: dict) -> str:
    return jwt.encode(claims, settings.jwt_secret, algorithm=ALGORITHM)


def issue_access(account: dict) -> str:
    now = _now()
    return _encode(
        {
            "sub": str(account["id"]),
            "username": account["username"],
            "role": account["role"],
            "type": "access",
            "jti": str(uuid.uuid4()),
            "iat": now,
            "exp": now + datetime.timedelta(minutes=ACCESS_MINUTES),
        }
    )


def issue_refresh(account: dict) -> str:
    now = _now()
    return _encode(
        {
            "sub": str(account["id"]),
            "type": "refresh",
            "jti": str(uuid.uuid4()),
            "iat": now,
            "exp": now + datetime.timedelta(days=REFRESH_DAYS),
        }
    )


def issue_pair(account: dict) -> dict:
    return {
        "access_token": issue_access(account),
        "refresh_token": issue_refresh(account),
        "token_type": "bearer",
    }


def decode(token: str, expected_type: str) -> dict:
    if not token:
        raise TokenRejected("Токен відсутній")
    try:
        # algorithms фіксує єдиний дозволений алгоритм: токен із
        # "alg": "none" відхиляється ще до перевірки підпису.
        claims = jwt.decode(token, settings.jwt_secret, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise TokenRejected("Термін дії токена минув") from None
    except jwt.InvalidTokenError:
        raise TokenRejected("Недійсний підпис або пошкоджений токен") from None

    if claims.get("type") != expected_type:
        raise TokenRejected("Надано некоректний тип токена")
    return claims


def revoke(token: str) -> None:
    _REVOKED.add(token)


def ensure_not_replayed(token: str) -> None:
    if token in _REVOKED:
        raise ReplayDetected(
            "Спроба повторного використання refresh-токена. "
            "Токен уже відкликано."
        )
