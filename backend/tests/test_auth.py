"""Authentication + core profile / academic-profile tests.

Runs against the real dev Supabase project + Postgres DB already configured
in backend/.env - see tests/conftest.py for the fixture/cleanup strategy.
"""
import uuid

from fastapi.testclient import TestClient

import app.routes.auth as auth_routes
from app.auth_config import FRONTEND_URL
from app.main import app
from app.supabase_client import supabase

TEST_PASSWORD = "PytestSmoke!12345"

PROTECTED_ROUTES = [
    ("GET", "/api/auth/me"),
    ("PATCH", "/api/profile/me"),
    ("GET", "/api/academic-profile/me"),
    ("GET", "/api/applications"),
    ("GET", "/api/documents"),
    ("GET", "/api/notifications"),
    ("GET", "/api/settings"),
    ("GET", "/api/saved-scholarships"),
    ("GET", "/api/matches"),
    ("POST", "/api/advisor/chat"),
]


def test_signup_creates_user_and_reports_confirmation_state(client):
    # Supabase's dev project enforces a real per-project email-sending rate
    # limit, exhausted by the volume of manual signup testing done on this
    # project. The endpoint correctly never leaks *why* signup failed (no
    # provider error text reaches the response either way) - so this test
    # asserts the safe-failure contract always, and the full creation
    # contract only when the call actually got through.
    email = f"pytest-signup-{uuid.uuid4().hex[:12]}@example.com"
    created_user_id = None
    try:
        response = client.post("/api/auth/signup", json={
            "email": email, "password": TEST_PASSWORD,
            "first_name": "Signup", "last_name": "Test",
        })
        assert response.status_code in (201, 400), response.text
        if response.status_code == 400:
            assert "detail" in response.json()
            assert "rate limit" not in response.text.lower()  # no provider detail leaked
            return
        body = response.json()
        created_user_id = body["user_id"]
        assert body["email"] == email
        assert isinstance(body["email_confirmation_required"], bool)
        assert body["message"]
    finally:
        if created_user_id:
            supabase.auth.admin.delete_user(created_user_id)


def test_signup_duplicate_email_does_not_leak_account_existence(client, user_a):
    # Supabase's anti-enumeration design means a signup attempt against an
    # existing, already-confirmed email does not return a distinguishing
    # error - callers can't tell "already registered" from "just created"
    # apart from the response. Confirm our endpoint passes that through
    # rather than adding its own "email already exists" error (which would
    # reintroduce the enumeration our provider deliberately avoids).
    _, _, existing_email = user_a
    response = client.post("/api/auth/signup", json={
        "email": existing_email, "password": TEST_PASSWORD,
        "first_name": "Dup", "last_name": "Test",
    })
    assert response.status_code in (200, 201, 400)
    assert "already" not in response.text.lower() and "exists" not in response.text.lower()


def test_login_success_sets_session_cookies(user_a):
    logged_in_client, _, _ = user_a
    # user_a's fixture already performed a successful login; confirm the
    # session actually works end to end.
    me = logged_in_client.get("/api/auth/me")
    assert me.status_code == 200
    assert "@example.com" in me.json()["email"]


def _set_cookie_headers_for(response, cookie_name: str):
    headers = response.headers.get_list("set-cookie")
    return [h for h in headers if h.startswith(f"{cookie_name}=")]


def test_production_cookie_config_is_secure_and_samesite_none(make_user, monkeypatch):
    # Render's default *.onrender.com service URLs are cross-site (onrender.com
    # is the public-suffix boundary), so a SameSite=Lax cookie is silently
    # dropped by the browser on the follow-up /api/auth/me fetch. Production
    # must use Secure + SameSite=None on every session cookie.
    monkeypatch.setattr(auth_routes, "COOKIE_SECURE", True)
    monkeypatch.setattr(auth_routes, "COOKIE_SAMESITE", "none")
    _, _, email = make_user()

    response = TestClient(app).post("/api/auth/login", json={"email": email, "password": TEST_PASSWORD})
    assert response.status_code == 200

    for cookie_name in (auth_routes.ACCESS_COOKIE, auth_routes.REFRESH_COOKIE):
        matches = _set_cookie_headers_for(response, cookie_name)
        assert matches, f"no Set-Cookie header found for {cookie_name}"
        header = matches[0].lower()
        assert "httponly" in header
        assert "secure" in header
        assert "samesite=none" in header
        assert "path=/" in header


def test_development_cookie_config_defaults_to_lax_and_not_secure(make_user, monkeypatch):
    # Local development must keep working exactly as before: no Secure
    # attribute (plain http://localhost), SameSite=Lax, and the session
    # must still authenticate the very next request on the same client.
    monkeypatch.setattr(auth_routes, "COOKIE_SECURE", False)
    monkeypatch.setattr(auth_routes, "COOKIE_SAMESITE", "lax")
    _, _, email = make_user()

    dev_client = TestClient(app)
    response = dev_client.post("/api/auth/login", json={"email": email, "password": TEST_PASSWORD})
    assert response.status_code == 200

    for cookie_name in (auth_routes.ACCESS_COOKIE, auth_routes.REFRESH_COOKIE):
        matches = _set_cookie_headers_for(response, cookie_name)
        assert matches, f"no Set-Cookie header found for {cookie_name}"
        header = matches[0].lower()
        assert "httponly" in header
        assert "secure" not in header
        assert "samesite=lax" in header

    me = dev_client.get("/api/auth/me")
    assert me.status_code == 200


def test_cors_allows_configured_frontend_origin_with_credentials(client):
    response = client.get("/api/health", headers={"Origin": FRONTEND_URL})
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == FRONTEND_URL
    assert response.headers.get("access-control-allow-credentials") == "true"


def test_login_wrong_password_is_rejected(client, user_a):
    _, _, email = user_a
    response = client.post("/api/auth/login", json={"email": email, "password": "WrongPassword!123"})
    assert response.status_code == 401
    assert "password" not in response.text.lower() or "invalid" in response.text.lower()


def test_login_unknown_email_is_rejected(client):
    response = client.post("/api/auth/login", json={
        "email": f"pytest-nonexistent-{uuid.uuid4().hex[:12]}@example.com",
        "password": "WhateverPassword!123",
    })
    assert response.status_code == 401


def test_get_me_returns_real_profile_fields(user_a):
    logged_in_client, user_id, email = user_a
    logged_in_client.patch("/api/profile/me", json={
        "first_name": "Alice", "last_name": "Tester",
        "nationality": "Testland", "country_of_residence": "Testopia",
    })
    me = logged_in_client.get("/api/auth/me")
    assert me.status_code == 200
    body = me.json()
    assert body["user_id"] == user_id
    assert body["email"] == email
    assert body["first_name"] == "Alice"
    assert body["nationality"] == "Testland"
    assert body["country_of_residence"] == "Testopia"


def test_logout_clears_session_and_blocks_protected_routes(user_a):
    logged_in_client, _, _ = user_a
    assert logged_in_client.get("/api/auth/me").status_code == 200

    logout = logged_in_client.post("/api/auth/logout")
    assert logout.status_code == 200

    after_logout = logged_in_client.get("/api/auth/me")
    assert after_logout.status_code == 401


PROTECTED_ROUTE_BODIES = {
    "/api/advisor/chat": {"message": "Hello"},
}


def test_all_protected_routes_require_authentication(client):
    for method, path in PROTECTED_ROUTES:
        body = PROTECTED_ROUTE_BODIES.get(path, {} if method in ("POST", "PATCH") else None)
        response = client.request(method, path, json=body)
        assert response.status_code == 401, f"{method} {path} should require auth, got {response.status_code}: {response.text}"


def test_refresh_session_succeeds_when_authenticated(user_a):
    logged_in_client, _, _ = user_a
    response = logged_in_client.post("/api/auth/refresh")
    assert response.status_code == 200


def test_refresh_session_fails_without_session(client):
    response = client.post("/api/auth/refresh")
    assert response.status_code == 401


def test_forgot_password_never_leaks_the_provider_error_reason(client, user_a):
    # NOTE: under an exhausted Supabase email quota, a known (real, must-send)
    # email and an unknown (no-send-needed) email CAN legitimately return
    # different status codes - Supabase's anti-enumeration design only
    # guarantees identical responses when it doesn't need to attempt a real
    # send. That is a real, quota-dependent enumeration side channel (see
    # audit report), not something this endpoint's own code controls. What
    # our code does guarantee, in every case: never surface Supabase's raw
    # error text - only our own fixed, generic detail message.
    _, _, existing_email = user_a
    known = client.post("/api/auth/forgot-password", json={"email": existing_email})
    unknown = client.post("/api/auth/forgot-password", json={"email": f"pytest-nope-{uuid.uuid4().hex[:12]}@example.com"})

    for response in (known, unknown):
        assert response.status_code in (200, 400)
        if response.status_code == 400:
            assert response.json()["detail"] == "Unable to send password reset email."
        else:
            assert "sent" in response.json()["message"].lower()


def test_academic_profile_blank_string_means_no_change(user_a):
    logged_in_client, _, _ = user_a
    logged_in_client.patch("/api/academic-profile/me", json={"gpa": "3.9"})

    # A blank string in a later PATCH must not wipe the previously saved value -
    # this is the exact historical bug fixed in the onboarding milestone.
    response = logged_in_client.patch("/api/academic-profile/me", json={"gpa": "", "field_of_study": "Physics"})
    assert response.status_code == 200
    body = response.json()
    assert body["gpa"] == "3.9"
    assert body["field_of_study"] == "Physics"


def test_academic_profile_update_persists_and_reads_back(user_a):
    logged_in_client, _, _ = user_a
    update = logged_in_client.patch("/api/academic-profile/me", json={
        "target_degree": "Master's", "language_test_type": "IELTS", "language_test_score": "7.5",
        "preferred_destinations": ["Germany", "Canada"],
    })
    assert update.status_code == 200

    fetched = logged_in_client.get("/api/academic-profile/me")
    assert fetched.status_code == 200
    body = fetched.json()
    assert body["target_degree"] == "Master's"
    assert body["language_test_score"] == "7.5"
    assert body["preferred_destinations"] == ["Germany", "Canada"]


def test_profile_and_academic_profile_are_isolated_between_users(user_a, user_b):
    client_a, _, _ = user_a
    client_b, _, _ = user_b

    client_a.patch("/api/profile/me", json={"nationality": "Wakandan"})
    client_a.patch("/api/academic-profile/me", json={"gpa": "4.0"})

    me_b = client_b.get("/api/auth/me").json()
    academic_b = client_b.get("/api/academic-profile/me").json()

    assert me_b["nationality"] != "Wakandan"
    assert academic_b["gpa"] != "4.0"
