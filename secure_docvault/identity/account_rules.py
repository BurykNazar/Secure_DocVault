"""Перевірка імені користувача, пошти та форми входу."""

from __future__ import annotations

import re

from .password_rules import problems as password_problems

NAME = re.compile(r"^[A-Za-z0-9_]{3,30}$")
MAIL = re.compile(r"^[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}$")


def validate_signup(
    username: str, email: str, password: str
) -> dict[str, list[str]]:
    issues: dict[str, list[str]] = {}
    name = username.strip()

    if not name:
        issues["username"] = ["Вкажіть ім'я користувача"]
    elif not NAME.fullmatch(name):
        issues["username"] = [
            "3–30 символів: латинські літери, цифри та «_»"
        ]

    address = email.strip()
    if not address:
        issues["email"] = ["Вкажіть електронну адресу"]
    elif ".." in address or not MAIL.fullmatch(address):
        issues["email"] = ["Перевірте формат електронної адреси"]

    weak = password_problems(password)
    if weak:
        issues["password"] = weak

    return issues


def validate_signin(username: str, password: str) -> dict[str, list[str]]:
    issues: dict[str, list[str]] = {}
    if not username.strip():
        issues["username"] = ["Вкажіть ім'я користувача"]
    if not password:
        issues["password"] = ["Вкажіть пароль"]
    return issues
