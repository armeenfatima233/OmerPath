"""Consolidated cross-user authorization/isolation sweep.

Every domain test file already asserts isolation for its own resource; this
file exercises all of them together for a single pair of users in one place,
as an explicit top-level isolation contract that's easy to audit on its own.
"""
import pytest
from sqlalchemy import select

from app.models.scholarship import Scholarship


def test_full_cross_user_isolation_sweep(db, user_a, user_b, mock_llm_reply):
    client_a, user_id_a, _ = user_a
    client_b, user_id_b, _ = user_b
    assert user_id_a != user_id_b

    scholarship_ids = list(db.scalars(select(Scholarship.id).where(Scholarship.status == "active").limit(2)).all())
    if len(scholarship_ids) < 2:
        pytest.skip("Need at least 2 active scholarships for the full isolation sweep.")
    scholarship_a, scholarship_b = scholarship_ids

    # --- A creates real data across every resource type ---
    client_a.patch("/api/profile/me", json={"nationality": "IsolationTestland"})
    client_a.patch("/api/academic-profile/me", json={"gpa": "3.99"})
    client_a.post(f"/api/saved-scholarships/{scholarship_a}")
    application_a = client_a.post("/api/applications", json={"scholarship_id": scholarship_a}).json()
    document_a = client_a.post(
        "/api/documents",
        files={"file": ("a-only.pdf", b"%PDF-1.4 a", "application/pdf")},
        data={"document_type": "Transcript"},
    ).json()
    client_a.patch("/api/settings", json={"weekly_digest": True})
    notification_a = client_a.get("/api/notifications").json()[0]  # from the application-created side effect

    # --- B must see none of it ---
    assert "IsolationTestland" not in client_b.get("/api/auth/me").json().values()
    assert client_b.get("/api/academic-profile/me").json()["gpa"] != "3.99"
    assert scholarship_a not in client_b.get("/api/saved-scholarships").json()["scholarship_ids"]
    assert client_b.get(f"/api/applications/{application_a['id']}").status_code == 404
    assert application_a["id"] not in [a["id"] for a in client_b.get("/api/applications").json()]
    assert client_b.get(f"/api/documents/{document_a['id']}/download").status_code == 404
    assert client_b.get("/api/documents").json() == []
    assert client_b.get("/api/settings").json()["weekly_digest"] is False
    assert client_b.get("/api/notifications").json() == []
    assert client_b.patch(f"/api/notifications/{notification_a['id']}/read").status_code == 404
    assert client_b.post("/api/advisor/chat", json={
        "message": "What's my application status?", "application_id": application_a["id"],
    }).status_code == 404

    # --- B cannot mutate A's data either ---
    assert client_b.patch(f"/api/applications/{application_a['id']}", json={"status": "Submitted"}).status_code == 404
    assert client_b.delete(f"/api/documents/{document_a['id']}").status_code == 404

    # --- A's data is untouched by all of B's attempts ---
    assert client_a.get(f"/api/applications/{application_a['id']}").json()["status"] == "Preparing"
    assert client_a.get(f"/api/documents/{document_a['id']}/download").status_code == 200

    # --- B creating the same-shaped data for itself does not collide with A's ---
    application_b = client_b.post("/api/applications", json={"scholarship_id": scholarship_b}).json()
    assert application_b["id"] != application_a["id"]
    ids_seen_by_a = [a["id"] for a in client_a.get("/api/applications").json()]
    assert application_b["id"] not in ids_seen_by_a
