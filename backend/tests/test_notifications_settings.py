"""Notifications (system-generated only) and settings: persistence + ownership."""


def test_notifications_are_created_only_as_side_effects(user_a, any_active_scholarship_id):
    client, _, _ = user_a
    assert client.get("/api/notifications").json() == []

    client.post("/api/applications", json={"scholarship_id": any_active_scholarship_id})

    notifications = client.get("/api/notifications").json()
    assert len(notifications) == 1
    assert notifications[0]["type"] == "application_started"
    assert notifications[0]["is_read"] is False


def test_no_endpoint_allows_directly_creating_a_notification(client):
    # There is deliberately no POST /api/notifications - only side-effect
    # creation from real actions (see app/notifications.py).
    response = client.post("/api/notifications", json={"type": "x", "title": "x", "message": "x"})
    assert response.status_code in (404, 405)


def test_mark_read_and_mark_all_read(user_a, any_active_scholarship_id):
    client, _, _ = user_a
    client.post("/api/applications", json={"scholarship_id": any_active_scholarship_id})
    notification = client.get("/api/notifications").json()[0]

    marked = client.patch(f"/api/notifications/{notification['id']}/read")
    assert marked.status_code == 200
    assert marked.json()["is_read"] is True

    client.patch(f"/api/applications/{client.get('/api/applications').json()[0]['id']}", json={"status": "Submitted"})
    mark_all = client.post("/api/notifications/mark-all-read")
    assert mark_all.status_code == 200
    assert all(n["is_read"] for n in mark_all.json())


def test_mark_read_on_another_users_notification_returns_404(user_a, user_b, any_active_scholarship_id):
    client_a, _, _ = user_a
    client_b, _, _ = user_b
    client_a.post("/api/applications", json={"scholarship_id": any_active_scholarship_id})
    notification_a = client_a.get("/api/notifications").json()[0]

    response = client_b.patch(f"/api/notifications/{notification_a['id']}/read")
    assert response.status_code == 404


def test_notifications_are_isolated_between_users(user_a, user_b, any_active_scholarship_id):
    client_a, _, _ = user_a
    client_b, _, _ = user_b
    client_a.post("/api/applications", json={"scholarship_id": any_active_scholarship_id})

    assert client_b.get("/api/notifications").json() == []


def test_settings_defaults_and_update_persists(user_a):
    client, _, _ = user_a
    defaults = client.get("/api/settings").json()
    assert defaults == {
        "deadline_reminders": True, "eligibility_changes": True, "advisor_nudges": True,
        "weekly_digest": False, "share_analytics": False,
    }

    updated = client.patch("/api/settings", json={"weekly_digest": True, "share_analytics": True})
    assert updated.status_code == 200
    assert updated.json()["weekly_digest"] is True
    assert updated.json()["share_analytics"] is True

    refetched = client.get("/api/settings").json()
    assert refetched["weekly_digest"] is True
    assert refetched["deadline_reminders"] is True  # untouched fields unchanged


def test_settings_are_isolated_between_users(user_a, user_b):
    client_a, _, _ = user_a
    client_b, _, _ = user_b

    client_a.patch("/api/settings", json={"weekly_digest": True})

    settings_b = client_b.get("/api/settings").json()
    assert settings_b["weekly_digest"] is False
