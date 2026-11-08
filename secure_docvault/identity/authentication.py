"""Вхід в обліковий запис."""

from __future__ import annotations

from ..transport.errors import InvalidLogin, ValidationRejected
from . import queries
from .account_rules import validate_signin
from .hashing import matches
from .models import SignIn
from .profile import public

# Однакове повідомлення для «немає такого користувача» і «невірний
# пароль»: не даємо змоги перелічувати облікові записи.
REJECTION = "Невірне ім'я користувача або пароль"


def sign_in(payload: SignIn) -> dict:
    username = payload.username.strip()

    issues = validate_signin(username, payload.password)
    if issues:
        raise ValidationRejected("Перевірте введені дані", fields=issues)

    account = queries.by_username(username)
    if account is None or not matches(payload.password, account["password_hash"]):
        raise InvalidLogin(REJECTION)

    return public(account)
