"""Складання застосунку Secure DocVault."""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from . import diagnostics
from .identity.routes import router as identity_routes
from .persistence.schema import install
from .settings import settings
from .site.pages import router as site_routes
from .transport.context import stamp
from .transport.handlers import attach
from .transport.health import router as status_routes

log = logging.getLogger("vault")


@asynccontextmanager
async def _lifecycle(_: FastAPI):
    install()
    log.info(
        "Secure DocVault доступний на http://%s:%s/", settings.host, settings.port
    )
    yield


def build() -> FastAPI:
    diagnostics.configure()
    # Схему створюємо одразу, щоб застосунок працював і без lifespan
    # (наприклад, у тестах).
    install()

    application = FastAPI(
        title="Secure DocVault API",
        version="0.1.0",
        description="Корпоративне сховище конфіденційних документів.",
        lifespan=_lifecycle,
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json",
    )

    attach(application)
    application.middleware("http")(stamp)
    application.include_router(identity_routes)
    application.include_router(status_routes)
    application.include_router(site_routes)

    if settings.client.is_dir():
        application.mount(
            "/static", StaticFiles(directory=settings.client), name="static"
        )
    else:  # pragma: no cover
        log.warning("Клієнтську частину не знайдено: %s", settings.client)

    return application


app = build()
