"""Rate limiting, WAF та Greylist для API."""

from __future__ import annotations

import logging
import time

from fastapi import Request
from fastapi.responses import JSONResponse

from .limiter import limiter
from .waf import inspect

log = logging.getLogger("vault.gate")

SKIP_PREFIXES = ("/static", "/api/docs", "/api/openapi.json")
BAN_SECONDS = 300
LOGIN_LIMIT = 5
API_LIMIT = 60

_banned: dict[str, float] = {}


def _client(request: Request) -> str:
    return request.client.host if request.client else "unknown"


def _ban_left(ip: str) -> int:
    until = _banned.get(ip)
    if not until:
        return 0
    left = int(until - time.time()) + 1
    if left <= 0:
        _banned.pop(ip, None)
        return 0
    return left


def reset() -> None:
    limiter.reset()
    _banned.clear()


def _deny(status: int, code: str, message: str, headers: dict | None = None):
    return JSONResponse(
        status_code=status,
        content={"ok": False, "error": {"code": code, "message": message}},
        headers=headers,
    )


async def guard(request: Request, call_next):
    path = request.url.path
    # Сторінка, статика й довідка не рахуються: інакше один захід у
    # браузері з'їдав би десятки запитів із ліміту.
    if not path.startswith("/api/") or path.startswith(SKIP_PREFIXES):
        return await call_next(request)
    if request.method == "OPTIONS":
        return await call_next(request)

    ip = _client(request)

    left = _ban_left(ip)
    if left:
        log.warning("[WAF] IP %s still blocked, %ss left (%s)", ip, left, path)
        return _deny(403, "ip_banned", f"Ваш IP заблоковано WAF. Спробуйте через {left} с.")

    body = await request.body()
    if body:
        async def receive(payload: bytes = body):
            return {"type": "http.request", "body": payload, "more_body": False}

        request = Request(request.scope, receive=receive)

    attack = inspect(path, request.url.query, body)
    if attack:
        _banned[ip] = time.time() + BAN_SECONDS
        log.error("[WAF] IP %s blocked: %s (%s)", ip, attack, path)
        return _deny(403, "waf_blocked", f"WAF заблокував запит ({attack}). IP заблоковано на 5 хв.")

    if path.endswith("/login"):
        limited, retry = limiter.hit(ip, "login", LOGIN_LIMIT)
        kind = "логін"
    else:
        limited, retry = limiter.hit(ip, "api", API_LIMIT)
        kind = "API"

    if limited:
        log.warning("[RATE LIMIT] IP %s %s, retry %ss (%s)", ip, kind, retry, path)
        return _deny(429, "rate_limited",
                     f"Перевищено ліміт запитів. Спробуйте через {retry} с.",
                     {"Retry-After": str(retry)})

    return await call_next(request)
