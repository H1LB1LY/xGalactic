"""Per-guild and per-user rate limiting."""

from __future__ import annotations

import os
import time
from collections import defaultdict
from dataclasses import dataclass, field


@dataclass
class RateLimiter:
    """Sliding-window rate limiter keyed by arbitrary string."""

    max_requests: int
    window_seconds: float = 60.0
    _hits: dict[str, list[float]] = field(default_factory=lambda: defaultdict(list))

    def check(self, key: str) -> bool:
        """Return True if request is allowed, False if rate limited."""
        now = time.monotonic()
        window_start = now - self.window_seconds
        hits = self._hits[key]
        self._hits[key] = [t for t in hits if t > window_start]
        if len(self._hits[key]) >= self.max_requests:
            return False
        self._hits[key].append(now)
        return True

    def retry_after(self, key: str) -> float:
        """Seconds until the oldest hit in window expires."""
        hits = self._hits.get(key, [])
        if not hits:
            return 0.0
        oldest = min(hits)
        return max(0.0, self.window_seconds - (time.monotonic() - oldest))


def default_limiters() -> tuple[RateLimiter, RateLimiter]:
    guild_max = int(os.getenv("RATE_LIMIT_GUILD", "60"))
    user_max = int(os.getenv("RATE_LIMIT_USER", "10"))
    return (
        RateLimiter(max_requests=guild_max),
        RateLimiter(max_requests=user_max),
    )
