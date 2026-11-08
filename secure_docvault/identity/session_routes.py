"""Оновлення пари токенів (Refresh Token Rotation)."""

from __future__ import annotations

from fastapi import APIRouter

from ..transport.errors import TokenRejected
from . import queries
from .models import RefreshPayload
from .tokens import decode, ensure_not_replayed, issue_pair, revoke

router = APIRouter(tags=["Сесія"])


@router.post("/api/v1/auth/refresh", summary="Оновити пару токенів")
def refresh(payload: RefreshPayload) -> dict:
    token = payload.refresh_token

    # Перевіряємо список відкликаних до криптографічної перевірки:
    # повторне надсилання вже використаного токена — ознака атаки.
    ensure_not_replayed(token)
    claims = decode(token, "refresh")
    revoke(token)

    try:
        account_id = int(claims["sub"])
    except (KeyError, TypeError, ValueError):
        raise TokenRejected("Некоректний токен") from None

    account = queries.by_id(account_id)
    if account is None:
        raise TokenRejected("Користувача не знайдено")

    return {"ok": True, **issue_pair(account)}
