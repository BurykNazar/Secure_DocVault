"""Ковзне вікно для обмеження частоти запитів."""

from __future__ import annotations

import time


class SlidingWindowLimiter:
    """Тримає мітки часу запитів для пари (IP, тип маршруту)."""

    def __init__(self) -> None:
        self._hits: dict[str, list[float]] = {}

    def hit(
        self, ip: str, kind: str, limit: int, window: int = 60
    ) -> tuple[bool, int]:
        key = f"{ip}:{kind}"
        now = time.monotonic()
        stamps = [t for t in self._hits.get(key, []) if now - t < window]

        if len(stamps) >= limit:
            self._hits[key] = stamps
            retry = int(window - (now - stamps[0])) + 1
            return True, max(1, retry)

        stamps.append(now)
        self._hits[key] = stamps
        return False, 0

    def reset(self) -> None:
        self._hits.clear()


limiter = SlidingWindowLimiter()
