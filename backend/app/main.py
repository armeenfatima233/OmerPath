import logging
import re

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth_config import APP_ENV, FRONTEND_URL
from app.routes import auth, profile

logger = logging.getLogger("omerpath.database")

# Matches credentials embedded in a connection URL, e.g. postgresql://user:pass@host
_URL_CREDENTIALS_RE = re.compile(r"//[^/@\s]+:[^/@\s]+@")
# Matches standalone password-like key=value pairs, e.g. password=secret
_PASSWORD_KV_RE = re.compile(r"(?i)(password|pwd)\s*=\s*[^\s&]+")


def _redact(message: str) -> str:
    message = _URL_CREDENTIALS_RE.sub("//***:***@", message)
    message = _PASSWORD_KV_RE.sub(r"\1=***", message)
    return message


def _classify_db_error(exc: Exception) -> str:
    text_blob = f"{type(exc).__name__} {exc}".lower()

    if "argumenterror" in text_blob or "could not parse" in text_blob or "invalid dsn" in text_blob:
        return "malformed URL"
    if "password authentication failed" in text_blob or "authentication" in text_blob:
        return "authentication/password"
    if any(
        keyword in text_blob
        for keyword in ("could not translate host name", "nodename nor servname", "getaddrinfo", "name or service not known")
    ):
        return "hostname/DNS"
    if "ssl" in text_blob:
        return "SSL"
    if "timed out" in text_blob or "timeout" in text_blob:
        return "network/timeout"
    if "connection refused" in text_blob:
        return "connection refused"
    if "database" in text_blob and "does not exist" in text_blob:
        return "database/user"
    if "role" in text_blob and "does not exist" in text_blob:
        return "database/user"

    return "unknown"


app = FastAPI(
    title="OmerPath API",
    description="Backend API for the OmerPath scholarship platform",
    version="1.0.0",
)

# Localhost development origins only. Production must use the real
# HTTPS frontend domain instead of these local addresses.
origins = [FRONTEND_URL]
if APP_ENV != "production":
    origins.extend(["http://localhost:3000", "http://127.0.0.1:3000"])
origins = list(dict.fromkeys(origins))

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=[
        "GET",
        "POST",
        "PATCH",
        "PUT",
        "DELETE",
        "OPTIONS",
    ],
    allow_headers=[
        "Accept",
        "Authorization",
        "Content-Type",
    ],
)

app.include_router(auth.router)
app.include_router(profile.router)


@app.get("/")
def read_root():
    return {"message": "OmerPath backend is running"}


@app.get("/api/health")
def health_check():
    return {"status": "healthy", "service": "omerpath-api"}


@app.get("/api/db-health")
def db_health_check(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {"status": "healthy", "database": "connected"}
    except Exception as exc:
        category = _classify_db_error(exc)
        sanitized_message = _redact(str(exc))
        logger.error(
            "Database health check failed | type=%s | category=%s | detail=%s",
            type(exc).__name__,
            category,
            sanitized_message,
        )
        return {"status": "unhealthy", "database": "unavailable"}
