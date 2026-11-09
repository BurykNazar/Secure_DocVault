"""Безпечні імена файлів і Content-Disposition."""

from __future__ import annotations

import re
import unicodedata
from urllib.parse import quote

_CONTROL = re.compile(r"[\x00-\x1f\x7f-\x9f]")
_UNSAFE = re.compile(r"[^A-Za-z0-9._ -]")
_FALLBACK = "document"
MAX_LENGTH = 120


def safe_name(raw_name: str | None) -> str:
    if not raw_name:
        return _FALLBACK
    name = raw_name.replace("\\", "/").split("/")[-1]
    name = _CONTROL.sub("", name).replace('"', "'").strip().strip(".")
    name = re.sub(r"\s+", " ", name)
    if not name:
        return _FALLBACK
    if len(name) > MAX_LENGTH:
        stem, dot, extension = name.rpartition(".")
        if dot and len(extension) <= 10:
            name = f"{stem[:MAX_LENGTH - len(extension) - 1]}.{extension}"
        else:
            name = name[:MAX_LENGTH]
    return name or _FALLBACK


def _ascii(name: str) -> str:
    normalized = unicodedata.normalize("NFKD", name)
    value = normalized.encode("ascii", "ignore").decode("ascii")
    return _UNSAFE.sub("_", value).strip(" ._")[:MAX_LENGTH] or _FALLBACK


def disposition(filename: str) -> str:
    name = safe_name(filename)
    fallback = _ascii(name)
    encoded = quote(name, safe="")
    return f'attachment; filename="{fallback}"; filename*=UTF-8\'\'{encoded}'
