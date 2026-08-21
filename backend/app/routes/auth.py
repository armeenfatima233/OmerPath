import logging
from dataclasses import dataclass
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth_config import (
    COOKIE_DOMAIN,
    COOKIE_SAMESITE,
    COOKIE_SECURE,
    FRONTEND_URL,
    PERSISTENT_SESSION_SECONDS,
)
from app.models.profile import Profile
from app.schemas.auth import (
    CurrentUserResponse,
    AuthCodeExchangeRequest,
    LoginRequest,
    LoginResponse,
    PasswordResetRequest,
    PasswordUpdateRequest,
    SignUpRequest,
    SignUpResponse,
)
from app.supabase_auth_client import (
    get_supabase_auth_client,
    request_password_reset_with_pkce,
    sign_up_with_pkce,
)

logger = logging.getLogger("omerpath.auth")

router = APIRouter(
    prefix="/api/auth",
    tags=["Authentication"],
)

ACCESS_COOKIE = "omerpath_access_token"
REFRESH_COOKIE = "omerpath_refresh_token"
PERSISTENCE_COOKIE = "omerpath_persistent_session"
PKCE_COOKIE = "omerpath_pkce_verifier"


@dataclass
class AuthenticatedSession:
    user: object
    access_token: str
    refresh_token: str | None
    persistent: bool


def _cookie_options(max_age: int | None = None) -> dict:
    options = {
        "httponly": True,
        "secure": COOKIE_SECURE,
        "samesite": COOKIE_SAMESITE,
        "path": "/",
    }
    if COOKIE_DOMAIN:
        options["domain"] = COOKIE_DOMAIN
    if max_age is not None:
        options["max_age"] = max_age
    return options


def _set_session_cookies(response: Response, session, persistent: bool) -> None:
    max_age = PERSISTENT_SESSION_SECONDS if persistent else None
    response.set_cookie(ACCESS_COOKIE, session.access_token, **_cookie_options(max_age))
    response.set_cookie(REFRESH_COOKIE, session.refresh_token, **_cookie_options(max_age))
    response.set_cookie(
        PERSISTENCE_COOKIE,
        "1" if persistent else "0",
        **_cookie_options(max_age),
    )


def _clear_auth_cookies(response: Response) -> None:
    delete_options = {"path": "/"}
    if COOKIE_DOMAIN:
        delete_options["domain"] = COOKIE_DOMAIN
    for key in (ACCESS_COOKIE, REFRESH_COOKIE, PERSISTENCE_COOKIE, PKCE_COOKIE):
        response.delete_cookie(key=key, **delete_options)


def get_authenticated_session(request: Request, response: Response) -> AuthenticatedSession:
    access_token = request.cookies.get(ACCESS_COOKIE)
    refresh_token = request.cookies.get(REFRESH_COOKIE)
    persistent = request.cookies.get(PERSISTENCE_COOKIE) == "1"
    client = get_supabase_auth_client()

    if access_token:
        try:
            user_response = client.auth.get_user(access_token)
            if user_response and user_response.user:
                return AuthenticatedSession(
                    user=user_response.user,
                    access_token=access_token,
                    refresh_token=refresh_token,
                    persistent=persistent,
                )
        except Exception:
            pass

    if refresh_token:
        try:
            auth_response = client.auth.refresh_session(refresh_token)
            if auth_response.session and auth_response.user:
                _set_session_cookies(response, auth_response.session, persistent)
                return AuthenticatedSession(
                    user=auth_response.user,
                    access_token=auth_response.session.access_token,
                    refresh_token=auth_response.session.refresh_token,
                    persistent=persistent,
                )
        except Exception as exc:
            logger.warning("Supabase session refresh failed | type=%s", type(exc).__name__)

    _clear_auth_cookies(response)
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated.",
    )


@router.post(
    "/signup",
    response_model=SignUpResponse,
    status_code=status.HTTP_201_CREATED,
)
def signup(payload: SignUpRequest, response: Response) -> SignUpResponse:
    try:
        auth_response, verifier = sign_up_with_pkce(
            email=str(payload.email),
            password=payload.password,
            first_name=payload.first_name,
            last_name=payload.last_name,
            redirect_to=f"{FRONTEND_URL}/auth/callback?flow=signup",
        )
    except Exception as exc:
        logger.error("Supabase signup failed | type=%s", type(exc).__name__)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unable to create account.",
        )

    if auth_response.user is None:
        logger.error("Supabase signup returned no user for email domain")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unable to create account.",
        )

    email_confirmation_required = auth_response.session is None

    if email_confirmation_required:
        response.set_cookie(
            PKCE_COOKIE,
            verifier,
            **_cookie_options(max_age=60 * 60),
        )
    else:
        _set_session_cookies(response, auth_response.session, persistent=False)

    if email_confirmation_required:
        message = "Account created. Please check your email to confirm your account."
    else:
        message = "Account created successfully."

    return SignUpResponse(
        user_id=auth_response.user.id,
        email=auth_response.user.email,
        email_confirmation_required=email_confirmation_required,
        message=message,
    )


@router.post(
    "/login",
    response_model=LoginResponse,
    status_code=status.HTTP_200_OK,
)
def login(payload: LoginRequest, response: Response) -> LoginResponse:
    client = get_supabase_auth_client()

    try:
        auth_response = client.auth.sign_in_with_password(
            {
                "email": payload.email,
                "password": payload.password,
            }
        )
    except Exception as exc:
        logger.error("Supabase login failed | type=%s", type(exc).__name__)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )

    if auth_response.user is None or auth_response.session is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )

    _set_session_cookies(response, auth_response.session, payload.remember)

    return LoginResponse(
        user_id=auth_response.user.id,
        email=auth_response.user.email,
        message="Signed in successfully.",
    )


@router.post(
    "/logout",
    status_code=status.HTTP_200_OK,
)
def logout(request: Request, response: Response) -> dict:
    access_token = request.cookies.get(ACCESS_COOKIE)
    refresh_token = request.cookies.get(REFRESH_COOKIE)

    if access_token and refresh_token:
        try:
            client = get_supabase_auth_client()
            client.auth.set_session(access_token, refresh_token)
            client.auth.sign_out()
        except Exception as exc:
            logger.error("Supabase logout failed | type=%s", type(exc).__name__)

    _clear_auth_cookies(response)

    return {"message": "Signed out successfully."}


@router.get(
    "/me",
    response_model=CurrentUserResponse,
)
def get_me(request: Request, response: Response, db: Session = Depends(get_db)) -> CurrentUserResponse:
    auth_session = get_authenticated_session(request, response)
    user_id = UUID(str(auth_session.user.id))

    profile = db.get(Profile, user_id)

    metadata = auth_session.user.user_metadata or {}

    return CurrentUserResponse(
        user_id=user_id,
        email=auth_session.user.email,
        first_name=profile.first_name if profile else metadata.get("first_name"),
        last_name=profile.last_name if profile else metadata.get("last_name"),
        nationality=profile.nationality if profile else None,
        country_of_residence=profile.country_of_residence if profile else None,
    )


@router.post("/refresh", status_code=status.HTTP_200_OK)
def refresh_session(request: Request, response: Response) -> dict:
    get_authenticated_session(request, response)
    return {"message": "Session refreshed."}


@router.post("/forgot-password", status_code=status.HTTP_200_OK)
def forgot_password(payload: PasswordResetRequest, response: Response) -> dict:
    try:
        verifier = request_password_reset_with_pkce(
            email=str(payload.email),
            redirect_to=f"{FRONTEND_URL}/auth/callback?flow=recovery",
        )
        response.set_cookie(PKCE_COOKIE, verifier, **_cookie_options(max_age=60 * 60))
    except Exception as exc:
        logger.warning("Supabase password reset request failed | type=%s", type(exc).__name__)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unable to send password reset email.",
        )
    return {"message": "If an account exists for that email, a reset link has been sent."}


@router.post("/exchange-code", status_code=status.HTTP_200_OK)
def exchange_code(payload: AuthCodeExchangeRequest, request: Request, response: Response) -> dict:
    verifier = request.cookies.get(PKCE_COOKIE)
    if not verifier:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Authentication link is invalid or expired.")
    try:
        client = get_supabase_auth_client()
        auth_response = client.auth.exchange_code_for_session(
            {"auth_code": payload.code, "code_verifier": verifier}
        )
        if not auth_response.session or not auth_response.user:
            raise ValueError("Supabase returned no session")
        _set_session_cookies(response, auth_response.session, persistent=False)
        delete_options = {"path": "/"}
        if COOKIE_DOMAIN:
            delete_options["domain"] = COOKIE_DOMAIN
        response.delete_cookie(key=PKCE_COOKIE, **delete_options)
    except Exception as exc:
        logger.warning("Supabase auth code exchange failed | type=%s", type(exc).__name__)
        _clear_auth_cookies(response)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Authentication link is invalid or expired.")
    return {"message": "Authentication confirmed."}


@router.post("/update-password", status_code=status.HTTP_200_OK)
def update_password(payload: PasswordUpdateRequest, request: Request, response: Response) -> dict:
    auth_session = get_authenticated_session(request, response)
    if not auth_session.refresh_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated.")
    try:
        client = get_supabase_auth_client()
        session_response = client.auth.set_session(
            auth_session.access_token,
            auth_session.refresh_token,
        )
        client.auth.update_user({"password": payload.password})
        if session_response.session:
            _set_session_cookies(response, session_response.session, auth_session.persistent)
    except Exception as exc:
        logger.warning("Supabase password update failed | type=%s", type(exc).__name__)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unable to update password.")
    return {"message": "Password updated successfully."}
