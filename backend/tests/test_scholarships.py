"""Public scholarship list/detail endpoints - no auth required."""
import uuid

from app.database import SessionLocal
from app.models.scholarship import Scholarship


def _make_draft_scholarship() -> str:
    """Inserts a throwaway non-active scholarship directly via the ORM (no
    route exists to create one - scholarships are curated, not user-created)
    and returns its id. Caller is responsible for deleting it."""
    db = SessionLocal()
    try:
        scholarship_id = f"pytest-draft-{uuid.uuid4().hex[:10]}"
        db.add(Scholarship(
            id=scholarship_id, name="Draft Scholarship", provider_name="Test Provider",
            status="draft",
        ))
        db.commit()
        return scholarship_id
    finally:
        db.close()


def _delete_scholarship(scholarship_id: str) -> None:
    db = SessionLocal()
    try:
        row = db.get(Scholarship, scholarship_id)
        if row is not None:
            db.delete(row)
            db.commit()
    finally:
        db.close()


def test_list_scholarships_requires_no_auth(client):
    response = client.get("/api/scholarships")
    assert response.status_code == 200
    body = response.json()
    assert "items" in body and "total" in body
    assert body["total"] == len(body["items"])


def test_list_scholarships_excludes_non_active(client):
    draft_id = _make_draft_scholarship()
    try:
        response = client.get("/api/scholarships")
        ids = [item["id"] for item in response.json()["items"]]
        assert draft_id not in ids
    finally:
        _delete_scholarship(draft_id)


def test_get_scholarship_detail_for_active_scholarship(client, any_active_scholarship_id):
    response = client.get(f"/api/scholarships/{any_active_scholarship_id}")
    assert response.status_code == 200
    assert response.json()["id"] == any_active_scholarship_id


def test_get_scholarship_detail_excludes_draft(client):
    draft_id = _make_draft_scholarship()
    try:
        response = client.get(f"/api/scholarships/{draft_id}")
        assert response.status_code == 404
    finally:
        _delete_scholarship(draft_id)


def test_get_scholarship_detail_invalid_id_returns_404(client):
    response = client.get(f"/api/scholarships/does-not-exist-{uuid.uuid4().hex[:8]}")
    assert response.status_code == 404
