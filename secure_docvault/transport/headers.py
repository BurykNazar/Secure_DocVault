"""Захисні HTTP-заголовки для кожної відповіді."""

from __future__ import annotations

APP_CSP = (
    "default-src 'self'; "
    "script-src 'self'; "
    "style-src 'self'; "
    "img-src 'self' data:; "
    "font-src 'self'; "
    "connect-src 'self'; "
    "object-src 'none'; "
    "frame-ancestors 'none'; "
    "base-uri 'self'; "
    "form-action 'self'"
)

# Scalar малює сторінку довідки інлайн-скриптами й скриптами з CDN,
# тому для /api/docs потрібна окрема, трохи ширша політика.
DOCS_CSP = (
    "default-src 'self'; "
    "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
    "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
    "img-src 'self' data: https://cdn.jsdelivr.net https://fastapi.tiangolo.com; "
    "font-src 'self' data: https://cdn.jsdelivr.net https://fonts.scalar.com; "
    "connect-src 'self' https://cdn.jsdelivr.net; "
    "worker-src 'self' blob:; "
    "object-src 'none'; "
    "frame-ancestors 'none'"
)


def _is_reference(path: str) -> bool:
    return path.startswith(("/api/docs", "/api/openapi.json"))


async def attach_headers(request, call_next):
    response = await call_next(request)

    response.headers["Content-Security-Policy"] = (
        DOCS_CSP if _is_reference(request.url.path) else APP_CSP
    )
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Strict-Transport-Security"] = (
        "max-age=31536000; includeSubDomains"
    )
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    if request.url.path.startswith("/static"):
        response.headers["Cache-Control"] = "no-cache"
    return response
