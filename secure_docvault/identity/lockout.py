"""Тимчасове блокування після серії невдалих спроб.

Стан зберігається в базі, тому перезапуск процесу не «скидає» захист.
"""

from __future__ import annotations

import math
from datetime import datetime, timedelta, timezone

from ..diagnostics import audit
from ..settings import settings
from ..transport.errors import AccountBlocked, InvalidLogin
from . import mutations

REJECTION = "Невірне ім'я користувача або пароль"


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _stamp(moment: datetime) -> str:
    return moment.astimezone(timezone.utc).isoformat(timespec="seconds").replace(
        "+00:00", "Z"
    )


def _parse(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def active_minutes(account: dict) -> int:
    """Скільки хвилин блокування ще лишилося (0 — доступу не заважає)."""
    until = _parse(account.get("locked_until"))
    if not until or until <= _now():
        return 0
    return max(1, math.ceil((until - _now()).total_seconds() / 60))


def clear_if_expired(account: dict) -> None:
    """Після завершення блокування лічильник починається з нуля."""
    until = _parse(account.get("locked_until"))
    if until and until <= _now():
        mutations.clear_failures(account["id"])
        account["failed_attempts"] = 0


def note_failure(account: dict, ip: str) -> None:
    attempt_no = int(account["failed_attempts"]) + 1

    if attempt_no >= settings.max_failures:
        until = _now() + timedelta(minutes=settings.lock_minutes)
        mutations.save_failure(account["id"], attempt_no, _stamp(until))
        audit(
            "account_blocked",
            ip=ip,
            username=account["username"],
            minutes=settings.lock_minutes,
        )
        raise AccountBlocked(
            "Забагато невдалих спроб. "
            f"Спробуйте через {settings.lock_minutes} хв."
        )

    mutations.save_failure(account["id"], attempt_no, None)
    audit(
        "sign_in_rejected",
        ip=ip,
        username=account["username"],
        reason="wrong_password",
        attempt=attempt_no,
    )
    raise InvalidLogin(REJECTION)
