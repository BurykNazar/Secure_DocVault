"""Складання застосунку Secure DocVault."""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from .identity.profile_routes import router as profile_routes
from .identity.routes import router as identity_routes
from .identity.session_routes import router as session_routes
from .persistence.schema import install
from .settings import settings
from .site.pages import router as site_routes
from .site.reference import router as reference_routes
from .transport.handlers import attach


@asynccontextmanager
async def _lifecycle(_: FastAPI):
    install()
    yield


def build() -> FastAPI:
    # Схему створюємо одразу, щоб застосунок працював і без lifespan
    # (наприклад, у тестах).
    install()

    application = FastAPI(
        title="Secure DocVault API",
        version="0.2.0",
        description="Корпоративне сховище конфіденційних документів.",
        lifespan=_lifecycle,
        docs_url=None,
        redoc_url=None,
        openapi_url="/api/openapi.json",
    )

    attach(application)
    application.include_router(identity_routes)
    application.include_router(session_routes)
    application.include_router(profile_routes)
    application.include_router(site_routes)
    application.include_router(reference_routes)

    if settings.client.is_dir():
        application.mount(
            "/static", StaticFiles(directory=settings.client), name="static"
        )

    return application


app = build()
