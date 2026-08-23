"""AI Advisor: auth, real-data grounding, unknown-data/ID-scrubbing behavior,
and safe provider-failure handling. The LLM call itself (app.advisor.
generate_json_reply) is mocked for all tests except the optional live_llm
one, so these never spend Groq quota or depend on model output wording.
"""
import json
import os
import uuid

import pytest

from app.advisor_errors import AdvisorConfigError, AdvisorProviderError

VALID_REPLY = json.dumps({
    "answer": "test answer", "warnings": [], "unknowns": [],
    "referenced_scholarship_ids": [], "referenced_application_ids": [],
})


def test_advisor_requires_authentication(client):
    response = client.post("/api/advisor/chat", json={"message": "Hello"})
    assert response.status_code == 401


def test_advisor_empty_message_returns_422(user_a, mock_llm_reply):
    client, _, _ = user_a
    response = client.post("/api/advisor/chat", json={"message": "   "})
    assert response.status_code == 422
    assert mock_llm_reply.calls == []  # never even reached the provider


def test_advisor_grounds_context_with_real_profile_data(user_a, mock_llm_reply):
    client, _, _ = user_a
    client.patch("/api/profile/me", json={"nationality": "Wakandan", "country_of_residence": "Wakanda"})
    client.patch("/api/academic-profile/me", json={"gpa": "3.95", "target_degree": "Master's"})

    response = client.post("/api/advisor/chat", json={"message": "What do you know about my profile?"})
    assert response.status_code == 200

    system_prompt = mock_llm_reply.calls[-1]["system_prompt"]
    assert "Wakandan" in system_prompt
    assert "Wakanda" in system_prompt
    assert "3.95" in system_prompt


def test_advisor_document_metadata_is_included_in_context(user_a, mock_llm_reply):
    client, _, _ = user_a
    client.post(
        "/api/documents",
        files={"file": ("my_transcript.pdf", b"%PDF-1.4 fake", "application/pdf")},
        data={"document_type": "Transcript"},
    )

    response = client.post("/api/advisor/chat", json={"message": "What documents do I have?"})
    assert response.status_code == 200
    assert "my_transcript.pdf" in mock_llm_reply.calls[-1]["system_prompt"]


def test_advisor_resolves_referenced_ids_from_real_data_not_the_model(user_a, mock_llm_reply, any_active_scholarship_id):
    client, _, _ = user_a
    mock_llm_reply.set_reply(json.dumps({
        "answer": "test", "warnings": [], "unknowns": [],
        "referenced_scholarship_ids": [any_active_scholarship_id],
        "referenced_application_ids": [],
    }))

    response = client.post("/api/advisor/chat", json={"message": "Tell me about this scholarship."})
    assert response.status_code == 200
    referenced = response.json()["referenced_scholarships"]
    assert len(referenced) == 1
    assert referenced[0]["id"] == any_active_scholarship_id
    assert referenced[0]["name"]  # resolved from the real DB row, not from the model


def test_advisor_ignores_fabricated_ids_the_model_invents(user_a, mock_llm_reply):
    # The model could hallucinate an id that isn't real or isn't the user's -
    # the route must silently drop it, never surface it as if it were real.
    client, _, _ = user_a
    fake_id = f"not-a-real-scholarship-{uuid.uuid4().hex[:8]}"
    mock_llm_reply.set_reply(json.dumps({
        "answer": "test", "warnings": [], "unknowns": [],
        "referenced_scholarship_ids": [fake_id],
        "referenced_application_ids": [str(uuid.uuid4())],
    }))

    response = client.post("/api/advisor/chat", json={"message": "Hello"})
    assert response.status_code == 200
    body = response.json()
    assert body["referenced_scholarships"] == []
    assert body["referenced_applications"] == []


def test_advisor_scholarship_focus_is_included_in_context(user_a, mock_llm_reply, any_active_scholarship_id):
    client, _, _ = user_a
    response = client.post("/api/advisor/chat", json={
        "message": "Why does this fit me?", "scholarship_id": any_active_scholarship_id,
    })
    assert response.status_code == 200
    assert f"CURRENT FOCUS: the student is currently viewing scholarship_id {any_active_scholarship_id}" in mock_llm_reply.calls[-1]["system_prompt"]


def test_advisor_invalid_scholarship_id_returns_404(user_a, mock_llm_reply):
    client, _, _ = user_a
    response = client.post("/api/advisor/chat", json={
        "message": "Why does this fit me?", "scholarship_id": "does-not-exist",
    })
    assert response.status_code == 404
    assert mock_llm_reply.calls == []


def test_advisor_application_focus_is_included_in_context(user_a, mock_llm_reply, any_active_scholarship_id):
    client, _, _ = user_a
    application = client.post("/api/applications", json={"scholarship_id": any_active_scholarship_id}).json()

    response = client.post("/api/advisor/chat", json={
        "message": "What's my next step?", "application_id": application["id"],
    })
    assert response.status_code == 200
    assert f"CURRENT FOCUS: the student is currently viewing application_id {application['id']}" in mock_llm_reply.calls[-1]["system_prompt"]


def test_advisor_invalid_application_id_returns_404(user_a, mock_llm_reply):
    client, _, _ = user_a
    response = client.post("/api/advisor/chat", json={
        "message": "What's my next step?", "application_id": str(uuid.uuid4()),
    })
    assert response.status_code == 404
    assert mock_llm_reply.calls == []


def test_advisor_cannot_see_another_users_application(user_a, user_b, mock_llm_reply, any_active_scholarship_id):
    client_a, _, _ = user_a
    client_b, _, _ = user_b
    application_a = client_a.post("/api/applications", json={"scholarship_id": any_active_scholarship_id}).json()

    response = client_b.post("/api/advisor/chat", json={
        "message": "What's my next step?", "application_id": application_a["id"],
    })
    assert response.status_code == 404


def test_advisor_provider_error_returns_502_without_leaking_detail(user_a, monkeypatch):
    client, _, _ = user_a

    def raise_provider_error(system_prompt, messages):
        raise AdvisorProviderError("Groq returned HTTP 503: capacity exceeded on internal cluster xyz")

    monkeypatch.setattr("app.advisor.generate_json_reply", raise_provider_error)

    response = client.post("/api/advisor/chat", json={"message": "Hello"})
    assert response.status_code == 502
    detail = response.json()["detail"]
    assert "capacity exceeded" not in detail
    assert "cluster xyz" not in detail


def test_advisor_missing_api_key_returns_503_without_leaking_detail(user_a, monkeypatch):
    client, _, _ = user_a

    def raise_config_error(system_prompt, messages):
        raise AdvisorConfigError("GROQ_API_KEY is not configured.")

    monkeypatch.setattr("app.advisor.generate_json_reply", raise_config_error)

    response = client.post("/api/advisor/chat", json={"message": "Hello"})
    assert response.status_code == 503
    assert "GROQ_API_KEY" not in response.json()["detail"]


def test_advisor_malformed_provider_json_returns_502(user_a, mock_llm_reply):
    client, _, _ = user_a
    mock_llm_reply.set_reply("this is not valid json {{{")

    response = client.post("/api/advisor/chat", json={"message": "Hello"})
    assert response.status_code == 502


def test_advisor_history_is_capped_before_being_sent(user_a, mock_llm_reply):
    client, _, _ = user_a
    long_history = [{"role": "user" if i % 2 == 0 else "assistant", "content": f"turn {i}"} for i in range(20)]

    response = client.post("/api/advisor/chat", json={"message": "Hello", "history": long_history})
    assert response.status_code == 200

    sent_messages = mock_llm_reply.calls[-1]["messages"]
    # Capped history (8) + the new user message.
    assert len(sent_messages) <= 9


@pytest.mark.live_llm
@pytest.mark.skipif(not os.getenv("GROQ_API_KEY"), reason="GROQ_API_KEY not configured")
def test_advisor_live_end_to_end_grounded_reply(user_a, any_active_scholarship_id):
    client, _, _ = user_a
    client.patch("/api/academic-profile/me", json={"target_degree": "Master's", "gpa": "3.8"})

    response = client.post("/api/advisor/chat", json={
        "message": "What is my fit score and eligibility for this scholarship?",
        "scholarship_id": any_active_scholarship_id,
    })
    assert response.status_code == 200
    body = response.json()
    assert body["answer"]
    assert "fit score" in body["answer"].lower()
