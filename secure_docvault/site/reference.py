"""Інтерактивна довідка API на базі Scalar.

Завантажує OpenAPI-схему застосунку та дозволяє надсилати запити
прямо зі сторінки — без Postman і без Swagger UI.
"""

from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from scalar_fastapi import get_scalar_api_reference

router = APIRouter(include_in_schema=False)


@router.api_route("/api/docs", methods=["GET", "HEAD"], response_class=HTMLResponse)
def reference() -> HTMLResponse:
    return get_scalar_api_reference(
        openapi_url="/api/openapi.json",
        title="Secure DocVault API",
        dark_mode=True,
        telemetry=False,
    )
