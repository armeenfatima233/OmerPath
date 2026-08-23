"""Minimal in-memory rate limiting - deliberately no external dependency
(no slowapi/redis/etc.), matching the project's "don't overengineer" stance.

Per-process, per-client-IP fixed-window counters. This is adequate for a
single backend instance, which is all this project runs today. If the
backend is ever horizontally scaled behind a load balancer, each instance
would enforce its own independent budget - move to a shared store (e.g.
Redis) at that point rather than before it's needed.
"""
import time
from collections import defaultdict
from threading import Lock

from fastapi import HTTPException, Request, status

_lock = Lock()
_buckets: dict[str, list[float]] = defaultdict(list)


def _client_ip(request: Request) -> str:
    # Only trust X-Forwarded-For when actually running behind a reverse
    # proxy/load balancer (production) - trusting it unconditionally would
    # let a direct client spoof its own rate-limit bucket.
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded and request.app.state.trust_proxy_headers:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def rate_limit(key: str, max_requests: int, window_seconds: int):
    """Returns a FastAPI dependency enforcing at most `max_requests` per
    `window_seconds` per client IP, independently for each `key` (so
    different routes don't share a budget)."""

    def _dependency(request: Request) -> None:
        bucket_key = f"{key}:{_client_ip(request)}"
        now = time.monotonic()
        with _lock:
            timestamps = _buckets[bucket_key]
            cutoff = now - window_seconds
            while timestamps and timestamps[0] < cutoff:
                timestamps.pop(0)
            if len(timestamps) >= max_requests:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Too many requests. Please try again later.",
                )
            timestamps.append(now)

    return _dependency


def reset_rate_limits() -> None:
    """Clears all buckets. Not used by the app itself - only by tests, since
    every in-process TestClient shares one fake client IP, which would
    otherwise make unrelated tests share a rate-limit budget."""
    with _lock:
        _buckets.clear()
