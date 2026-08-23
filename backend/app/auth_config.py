import os

from dotenv import load_dotenv

load_dotenv()


def _as_bool(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


APP_ENV = os.getenv("APP_ENV", "development").strip().lower()
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000").rstrip("/")
COOKIE_SECURE = _as_bool(
    os.getenv("AUTH_COOKIE_SECURE"),
    default=APP_ENV == "production",
)
COOKIE_SAMESITE = os.getenv("AUTH_COOKIE_SAMESITE", "lax").strip().lower()
if COOKIE_SAMESITE not in {"lax", "strict", "none"}:
    COOKIE_SAMESITE = "lax"
COOKIE_DOMAIN = os.getenv("AUTH_COOKIE_DOMAIN") or None
PERSISTENT_SESSION_SECONDS = int(
    os.getenv("AUTH_SESSION_MAX_AGE_SECONDS", str(30 * 24 * 60 * 60))
)
# Only trust X-Forwarded-For (used for rate-limit bucketing) when actually
# deployed behind a reverse proxy/load balancer that sets it - trusting it
# from direct/dev clients would let a caller spoof its own rate-limit bucket.
TRUST_PROXY_HEADERS = _as_bool(
    os.getenv("TRUST_PROXY_HEADERS"),
    default=APP_ENV == "production",
)

