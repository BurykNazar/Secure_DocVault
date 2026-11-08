"""Створення облікового запису."""

from __future__ import annotations

import logging
import sqlite3

from ..diagnostics import audit
from ..transport.errors import DuplicateAccount, ValidationRejected
from . import mutations, queries
from .account_rules import validate_signup
from .hashing import seal
from .models import SignUp
from .profile import public

log = logging.getLogger("vault.identity")


def sign_up(payload: SignUp, ip: str) -> dict:
    username = payload.username.strip()
    email = payload.email.strip().lower()

    issues = validate_signup(username, email, payload.password)
    if issues:
        audit(
            "sign_up_rejected",
            ip=ip,
            username=username,
            reason="validation",
            fields=sorted(issues),
        )
        raise ValidationRejected("Перевірте введені дані", fields=issues)

    if queries.by_username(username):
        raise DuplicateAccount(
            "Такий обліковий запис уже існує",
            fields={"username": ["Це ім'я вже зайняте"]},
        )
    if queries.by_email(email):
        raise DuplicateAccount(
            "Такий обліковий запис уже існує",
            fields={"email": ["Ця пошта вже використовується"]},
        )

    digest, salt = seal(payload.password)
    try:
        account_id = mutations.insert_account(username, email, digest, salt)
    except sqlite3.IntegrityError:
        # Гонка двох одночасних реєстрацій: унікальний індекс — остання
        # лінія оборони.
        raise DuplicateAccount(
            "Такий обліковий запис уже існує",
            fields={
                "username": ["Можливо, ім'я вже зайняте"],
                "email": ["Можливо, пошта вже використовується"],
            },
        ) from None

    account = queries.by_id(account_id)
    assert account is not None
    audit("account_created", ip=ip, account=account_id, username=username)
    log.info("Створено обліковий запис «%s»", username)
    return public(account)
