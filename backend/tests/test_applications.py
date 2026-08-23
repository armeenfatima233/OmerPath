"""Applications: create, duplicate prevention, status transitions, progress,
and cross-user isolation."""
from sqlalchemy import select

from app.models.scholarship import Scholarship


def _two_active_scholarship_ids(db) -> list[str]:
    ids = list(db.scalars(select(Scholarship.id).where(Scholarship.status == "active").limit(2)).all())
    if len(ids) < 2:
        import pytest
        pytest.skip("Need at least 2 active scholarships for this test.")
    return ids


def test_create_application_defaults(user_a, any_active_scholarship_id):
    client, _, _ = user_a
    response = client.post("/api/applications", json={"scholarship_id": any_active_scholarship_id})
    assert response.status_code == 201
    body = response.json()
    assert body["scholarship_id"] == any_active_scholarship_id
    assert body["status"] == "Preparing"
    assert body["progress"] == 0


def test_create_duplicate_application_returns_existing_not_new(user_a, any_active_scholarship_id):
    client, _, _ = user_a
    first = client.post("/api/applications", json={"scholarship_id": any_active_scholarship_id})
    second = client.post("/api/applications", json={"scholarship_id": any_active_scholarship_id})

    assert first.status_code == 201
    assert second.status_code == 200
    assert first.json()["id"] == second.json()["id"]

    listed = client.get("/api/applications").json()
    matching = [a for a in listed if a["scholarship_id"] == any_active_scholarship_id]
    assert len(matching) == 1


def test_create_application_invalid_scholarship_id_returns_404(user_a):
    client, _, _ = user_a
    response = client.post("/api/applications", json={"scholarship_id": "does-not-exist"})
    assert response.status_code == 404


def test_status_transition_to_ready_to_apply_bumps_progress(user_a, any_active_scholarship_id):
    client, _, _ = user_a
    created = client.post("/api/applications", json={"scholarship_id": any_active_scholarship_id}).json()

    response = client.patch(f"/api/applications/{created['id']}", json={"status": "Ready to apply"})
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "Ready to apply"
    assert body["progress"] >= 90
    assert body["next_action"]


def test_status_transition_to_submitted_sets_full_progress(user_a, any_active_scholarship_id):
    client, _, _ = user_a
    created = client.post("/api/applications", json={"scholarship_id": any_active_scholarship_id}).json()

    response = client.patch(f"/api/applications/{created['id']}", json={"status": "Submitted"})
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "Submitted"
    assert body["progress"] == 100


def test_status_transition_back_to_preparing_caps_progress(user_a, any_active_scholarship_id):
    client, _, _ = user_a
    created = client.post("/api/applications", json={"scholarship_id": any_active_scholarship_id}).json()
    client.patch(f"/api/applications/{created['id']}", json={"status": "Submitted"})

    response = client.patch(f"/api/applications/{created['id']}", json={"status": "Preparing"})
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "Preparing"
    assert body["progress"] <= 89


def test_invalid_status_value_is_rejected(user_a, any_active_scholarship_id):
    client, _, _ = user_a
    created = client.post("/api/applications", json={"scholarship_id": any_active_scholarship_id}).json()

    response = client.patch(f"/api/applications/{created['id']}", json={"status": "Accepted!!!"})
    assert response.status_code == 422


def test_get_nonexistent_application_returns_404(user_a):
    client, _, _ = user_a
    response = client.get("/api/applications/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404


def test_applications_are_isolated_between_users(db, user_a, user_b):
    client_a, _, _ = user_a
    client_b, _, _ = user_b
    scholarship_ids = _two_active_scholarship_ids(db)

    created_a = client_a.post("/api/applications", json={"scholarship_id": scholarship_ids[0]}).json()

    # B cannot read A's application by id.
    get_by_b = client_b.get(f"/api/applications/{created_a['id']}")
    assert get_by_b.status_code == 404

    # B cannot update A's application by id.
    patch_by_b = client_b.patch(f"/api/applications/{created_a['id']}", json={"status": "Submitted"})
    assert patch_by_b.status_code == 404

    # B's own application list never includes A's application.
    b_own = client_b.post("/api/applications", json={"scholarship_id": scholarship_ids[1]}).json()
    listed_b = client_b.get("/api/applications").json()
    ids_b = [a["id"] for a in listed_b]
    assert created_a["id"] not in ids_b
    assert b_own["id"] in ids_b
