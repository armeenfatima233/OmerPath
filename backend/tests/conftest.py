"""Shared pytest fixtures for the OmerPath backend test suite.

These are integration-style tests, not unit tests with mocked infrastructure:
they run the real FastAPI app in-process (via TestClient) against the real
dev Supabase project and Postgres database already configured in
backend/.env - the same project used for every manual smoke test throughout
this project. Test users are created via the Supabase admin API and deleted
in a fixture teardown; ON DELETE CASCADE on every user_id FK means deleting
the auth user cleans up every row it owns.

Never point this suite at a production database or Supabase project.
"""
import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select

from app.database import SessionLocal
from app.main import app
from app.models.scholarship import Scholarship
from app.rate_limit import reset_rate_limits
from app.supabase_client import supabase

TEST_PASSWORD = "PytestSmoke!12345"


@pytest.fixture(autouse=True)
def _reset_rate_limits():
    """Every in-process TestClient reports the same fake client IP, so
    without this, unrelated tests would share one rate-limit budget on
    routes like /api/auth/login that every user fixture calls."""
    reset_rate_limits()
    yield
    reset_rate_limits()


@pytest.fixture
def db():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client():
    """Unauthenticated TestClient - for public routes and 401 checks."""
    return TestClient(app)


@pytest.fixture
def make_user():
    """Factory fixture: creates a throwaway confirmed Supabase user, logs it
    in on a fresh TestClient, and guarantees admin deletion during teardown
    even if the test fails or raises."""
    created_user_ids = []

    def _make(first_name: str = "Pytest", last_name: str = "User"):
        email = f"pytest-{uuid.uuid4().hex[:12]}@example.com"
        user_resp = supabase.auth.admin.create_user({
            "email": email,
            "password": TEST_PASSWORD,
            "email_confirm": True,
            "user_metadata": {"first_name": first_name, "last_name": last_name},
        })
        user_id = str(user_resp.user.id)
        created_user_ids.append(user_id)

        test_client = TestClient(app)
        login = test_client.post("/api/auth/login", json={"email": email, "password": TEST_PASSWORD})
        assert login.status_code == 200, f"fixture login failed: {login.status_code} {login.text}"

        return test_client, user_id, email

    yield _make

    for user_id in created_user_ids:
        try:
            supabase.auth.admin.delete_user(user_id)
        except Exception:
            # Best-effort cleanup - a failed delete here must not fail the test
            # that already ran and asserted; the account is a disposable
            # pytest-*@example.com throwaway either way.
            pass


@pytest.fixture
def user_a(make_user):
    """(client, user_id, email) for a first throwaway user."""
    return make_user("Alice", "PytestTest")


@pytest.fixture
def user_b(make_user):
    """(client, user_id, email) for a second, independent throwaway user -
    for cross-user isolation checks."""
    return make_user("Bob", "PytestTest")


@pytest.fixture
def any_active_scholarship_id(db):
    """An id from the real, currently-active scholarship dataset. Tests use
    this instead of hardcoding a specific scholarship so they don't break if
    the curated dataset changes - tests that need a *specific* scholarship's
    eligibility fields use test_matching.py's in-memory objects instead."""
    scholarship_id = db.scalar(select(Scholarship.id).where(Scholarship.status == "active").limit(1))
    if scholarship_id is None:
        pytest.skip("No active scholarships in the database - seed data required for this test.")
    return scholarship_id


@pytest.fixture
def mock_llm_reply(monkeypatch):
    """Replaces app.advisor.generate_json_reply with a fake that returns a
    caller-supplied JSON string, and records every call's (system_prompt,
    messages) for assertions - so Advisor tests never hit the real Groq API
    (or spend quota) unless explicitly marked @pytest.mark.live_llm."""
    calls = []
    reply_holder = {"text": '{"answer": "test", "warnings": [], "unknowns": [], "referenced_scholarship_ids": [], "referenced_application_ids": []}'}

    def _fake_generate(system_prompt, messages):
        calls.append({"system_prompt": system_prompt, "messages": messages})
        return reply_holder["text"]

    monkeypatch.setattr("app.advisor.generate_json_reply", _fake_generate)

    class Handle:
        def set_reply(self, text: str):
            reply_holder["text"] = text

        @property
        def calls(self):
            return calls

    return Handle()
