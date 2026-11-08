"""Єдиний обробник помилок на межі HTTP."""

from __future__ import annotations

import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as HttpError

from .errors import DomainError

log = logging.getLogger("vault.http")


def _body(code: str, message: str, fields: dict | None = None) -> dict:
    error: dict[str, object] = {"code": code, "message": message}
    if fields:
        error["fields"] = fields
    return {"ok": False, "error": error}


def attach(application: FastAPI) -> None:
    @application.exception_handler(DomainError)
    async def _domain(_: Request, error: DomainError) -> JSONResponse:
        return error.respond()

    @application.exception_handler(RequestValidationError)
    async def _invalid(_: Request, error: RequestValidationError) -> JSONResponse:
        fields: dict[str, list[str]] = {}
        for item in error.errors():
            parts = [part for part in item.get("loc", ()) if isinstance(part, str)]
            fields.setdefault(parts[-1] if parts else "payload", []).append(
                "Некоректне значення"
            )
        return JSONResponse(
            status_code=400,
            content=_body("validation_failed", "Перевірте введені дані", fields),
        )

    @application.exception_handler(HttpError)
    async def _http(_: Request, error: HttpError) -> JSONResponse:
        message = error.detail if isinstance(error.detail, str) else "Помилка запиту"
        return JSONResponse(
            status_code=error.status_code,
            content=_body("http_error", message),
            headers=error.headers,
        )

    @application.exception_handler(Exception)
    async def _unknown(_: Request, error: Exception) -> JSONResponse:
        log.exception("Непередбачена помилка", exc_info=error)
        return JSONResponse(
            status_code=500,
            content=_body("internal_error", "Внутрішня помилка сервера"),
        )
