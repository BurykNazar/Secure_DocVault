"""Вхід в обліковий запис."""

from __future__ import annotations

import logging

from ..diagnostics import audit
from ..transport.errors import AccessDenied, AccountBlocked, InvalidLogin, ValidationRejected
from . import mutations, queries
from .account_rules import validate_signin
from .hashing import matches, spend_comparison_time
from .lockout import REJECTION, active_minutes, clear_if_expired, note_failure
from .models import SignIn
from .profile import public

log = logging.getLogger("vault.identity")


def sign_in(payload: SignIn, ip: str) -> dict:
    username = payload.username.strip()

    issues = validate_signin(username, payload.password)
    if issues:
        raise ValidationRejected("Перевірте введені дані", fields=issues)

    account = queries.by_username(username)
    if account is None:
        spend_comparison_time(payload.password)
        audit(
            "sign_in_rejected",
            ip=ip,
            username=username,
            reason="unknown_account",
        )
        raise InvalidLogin(REJECTION)

    if not account["is_active"]:
        audit("sign_in_rejected", ip=ip, username=username, reason="inactive")
        raise AccessDenied("Обліковий запис недоступний")

    minutes = active_minutes(account)
    if minutes:
        audit(
            "sign_in_rejected",
            ip=ip,
            username=username,
            reason="blocked",
            minutes=minutes,
        )
        raise AccountBlocked(
            f"Обліковий запис тимчасово заблоковано. "
            f"Спробуйте через {minutes} хв."
        )

    clear_if_expired(account)

    if not matches(payload.password, account["password_hash"]):
        note_failure(account, ip)

    mutations.clear_failures(account["id"])
    audit("sign_in", ip=ip, account=account["id"], username=account["username"])
    log.info("Вхід виконано: %s", account["username"])
    return public(account)
