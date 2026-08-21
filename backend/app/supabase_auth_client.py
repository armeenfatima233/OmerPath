# Auth/RLS client for normal user authentication and RLS-controlled
# operations (uses the publishable key). Privileged server-only operations
# use the separate server-only client in supabase_client.py.
import os

from dotenv import load_dotenv
from supabase import Client, create_client
from supabase_auth.helpers import (
    generate_pkce_challenge,
    generate_pkce_verifier,
    parse_auth_response,
)
from supabase_auth.types import AuthResponse

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_PUBLISHABLE_KEY = os.getenv("SUPABASE_PUBLISHABLE_KEY")

if not SUPABASE_URL or not SUPABASE_PUBLISHABLE_KEY:
    raise RuntimeError(
        "SUPABASE_URL and SUPABASE_PUBLISHABLE_KEY must be set in the environment"
    )


def get_supabase_auth_client() -> Client:
    return create_client(
        SUPABASE_URL,
        SUPABASE_PUBLISHABLE_KEY,
    )


def sign_up_with_pkce(
    email: str,
    password: str,
    first_name: str,
    last_name: str,
    redirect_to: str,
) -> tuple[AuthResponse, str]:
    client = get_supabase_auth_client()
    verifier = generate_pkce_verifier()
    auth_response = parse_auth_response(
        client.auth._request(
            "POST",
            "signup",
            body={
                "email": email,
                "password": password,
                "data": {"first_name": first_name, "last_name": last_name},
                "code_challenge": generate_pkce_challenge(verifier),
                "code_challenge_method": "s256",
            },
            redirect_to=redirect_to,
        )
    )
    return auth_response, verifier


def request_password_reset_with_pkce(
    email: str,
    redirect_to: str,
) -> str:
    client = get_supabase_auth_client()
    verifier = generate_pkce_verifier()
    client.auth._request(
        "POST",
        "recover",
        body={
            "email": email,
            "code_challenge": generate_pkce_challenge(verifier),
            "code_challenge_method": "s256",
        },
        redirect_to=redirect_to,
    )
    return verifier
