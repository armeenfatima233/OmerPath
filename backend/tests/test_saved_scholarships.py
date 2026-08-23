"""Saved scholarships: save, duplicate prevention, unsave, cross-user isolation."""


def test_save_and_list(user_a, any_active_scholarship_id):
    client, _, _ = user_a
    response = client.post(f"/api/saved-scholarships/{any_active_scholarship_id}")
    assert response.status_code == 200
    assert any_active_scholarship_id in response.json()["scholarship_ids"]

    listed = client.get("/api/saved-scholarships")
    assert any_active_scholarship_id in listed.json()["scholarship_ids"]


def test_saving_twice_does_not_duplicate(user_a, any_active_scholarship_id):
    client, _, _ = user_a
    client.post(f"/api/saved-scholarships/{any_active_scholarship_id}")
    second = client.post(f"/api/saved-scholarships/{any_active_scholarship_id}")

    assert second.status_code == 200
    ids = second.json()["scholarship_ids"]
    assert ids.count(any_active_scholarship_id) == 1


def test_unsave_removes_it(user_a, any_active_scholarship_id):
    client, _, _ = user_a
    client.post(f"/api/saved-scholarships/{any_active_scholarship_id}")

    response = client.delete(f"/api/saved-scholarships/{any_active_scholarship_id}")
    assert response.status_code == 200
    assert any_active_scholarship_id not in response.json()["scholarship_ids"]


def test_unsave_when_not_saved_is_a_no_op(user_a, any_active_scholarship_id):
    client, _, _ = user_a
    response = client.delete(f"/api/saved-scholarships/{any_active_scholarship_id}")
    assert response.status_code == 200
    assert response.json()["scholarship_ids"] == []


def test_save_invalid_scholarship_id_returns_404(user_a):
    client, _, _ = user_a
    response = client.post("/api/saved-scholarships/does-not-exist")
    assert response.status_code == 404


def test_saved_scholarships_are_isolated_between_users(user_a, user_b, any_active_scholarship_id):
    client_a, _, _ = user_a
    client_b, _, _ = user_b

    client_a.post(f"/api/saved-scholarships/{any_active_scholarship_id}")

    saved_b = client_b.get("/api/saved-scholarships").json()["scholarship_ids"]
    assert any_active_scholarship_id not in saved_b
