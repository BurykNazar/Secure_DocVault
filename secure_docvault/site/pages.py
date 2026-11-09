"""Віддача клієнтської частини."""

from fastapi import APIRouter
from fastapi.responses import FileResponse

from ..settings import settings
from ..transport.errors import MissingResource

router = APIRouter(include_in_schema=False)


@router.api_route("/", methods=["GET", "HEAD"], response_class=FileResponse)
def home() -> FileResponse:
    index = settings.client / "index.html"
    if not index.is_file():
        raise MissingResource("Клієнтську частину не знайдено")
    return FileResponse(
        index,
        media_type="text/html; charset=utf-8",
        headers={"Cache-Control": "no-store"},
    )
