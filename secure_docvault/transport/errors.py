"""Доменні помилки та їхнє HTTP-представлення.

Одна структура відповіді для всіх випадків::

    {"ok": false, "error": {"code": "…", "message": "…", "fields": {…}}}

Клієнт не розбирає різні формати FastAPI, а лише показує message та
підсвічує поля з fields.
"""

from __future__ import annotations

from fastapi.responses import JSONResponse


class DomainError(Exception):
    status = 400
    code = "bad_request"
    brief = "Некоректний запит"

    def __init__(
        self, message: str | None = None, *, fields: dict[str, list[str]] | None = None
    ) -> None:
        self.message = message or self.brief
        self.fields = fields or {}
        super().__init__(self.message)

    def respond(self) -> JSONResponse:
        error: dict[str, object] = {"code": self.code, "message": self.message}
        if self.fields:
            error["fields"] = self.fields
        return JSONResponse(
            status_code=self.status, content={"ok": False, "error": error}
        )


class ValidationRejected(DomainError):
    status = 400
    code = "validation_failed"
    brief = "Перевірте введені дані"


class InvalidLogin(DomainError):
    status = 401
    code = "invalid_credentials"
    brief = "Невірні облікові дані"


class MissingResource(DomainError):
    status = 404
    code = "not_found"
    brief = "Ресурс не знайдено"


class DuplicateAccount(DomainError):
    status = 409
    code = "account_exists"
    brief = "Обліковий запис уже існує"


class TokenRejected(DomainError):
    status = 401
    code = "invalid_token"
    brief = "Недійсний токен"


class ReplayDetected(DomainError):
    status = 401
    code = "token_reuse"
    brief = "Токен уже використано"
