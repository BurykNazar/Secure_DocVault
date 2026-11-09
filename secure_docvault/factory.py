"""Складання застосунку Secure DocVault."""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .comments.routes import router as comment_routes
from .identity.profile_routes import router as profile_routes
from .identity.routes import router as identity_routes
from .identity.session_routes import router as session_routes
from .persistence.schema import install
from .settings import settings
from .site.pages import router as site_routes
from .site.reference import router as reference_routes
from .transport.handlers import attach
from .transport.headers import attach_headers


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
        version="0.3.0",
        description="Корпоративне сховище конфіденційних документів.",
        lifespan=_lifecycle,
        docs_url=None,
        redoc_url=None,
        openapi_url="/api/openapi.json",
    )

    attach(application)
    application.add_middleware(
        CORSMiddleware,
        allow_origins=list(settings.cors_origins),
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type"],
    )
    application.middleware("http")(attach_headers)

    application.include_router(identity_routes)
    application.include_router(session_routes)
    application.include_router(profile_routes)
    application.include_router(comment_routes)
    application.include_router(site_routes)
    application.include_router(reference_routes)

    if settings.client.is_dir():
        application.mount(
            "/static", StaticFiles(directory=settings.client), name="static"
        )

    return application


app = build()
