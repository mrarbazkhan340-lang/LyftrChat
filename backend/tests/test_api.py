
import pytest
from fastapi.testclient import TestClient

from app import main


@pytest.fixture
def client(monkeypatch):
    """Create an isolated API test environment."""

    sessions = {}
    messages = {}

    def fake_create_session(session_id, system_prompt=None):
        sessions[session_id] = {
            "session_id": session_id,
            "system_prompt": system_prompt,
        }
        messages[session_id] = []

    def fake_get_session(session_id):
        return sessions.get(session_id)

    def fake_update_system_prompt(session_id, system_prompt):
        sessions[session_id]["system_prompt"] = system_prompt

    def fake_add_message(session_id, role, content, metadata=None):
        messages[session_id].append({
            "role": role,
            "content": content,
            "metadata": metadata,
        })

    def fake_get_messages(session_id):
        return messages.get(session_id, [])

    def fake_generate_response(
        user_message,
        history,
        system_prompt=None,
        simulated_failures=None,
    ):
        if simulated_failures and "*" in simulated_failures:
            raise main.AllProvidersUnavailable()

        return {
            "reply": f"Test reply to: {user_message}",
            "metadata": {
                "resolution_source": "LIVE_INFERENCE",
                "model": "test-model",
                "input_tokens": 10,
                "output_tokens": 8,
                "key_id": "key_1",
                "fallback_attempts": 0,
            },
        }

    monkeypatch.setattr(main, "create_session", fake_create_session)
    monkeypatch.setattr(main, "get_session", fake_get_session)
    monkeypatch.setattr(main, "update_system_prompt", fake_update_system_prompt)
    monkeypatch.setattr(main, "add_message", fake_add_message)
    monkeypatch.setattr(main, "get_messages", fake_get_messages)
    monkeypatch.setattr(main, "generate_response", fake_generate_response)
    monkeypatch.setattr(main, "check_database", lambda: True)
    monkeypatch.setattr(main, "API_KEY_POOL", [
        {"key_id": "key_1", "api_key": "test-key-1"},
        {"key_id": "key_2", "api_key": "test-key-2"},
    ])
    monkeypatch.setattr(main, "ENABLE_FAILURE_SIMULATION", True)

    return TestClient(main.app)


def test_health_check(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "keys_configured": 2,
        "cache_enabled": True,
    }


def test_chat_creates_session_and_returns_reply(client):
    response = client.post(
        "/chat",
        json={
            "session_id": "test-session",
            "message": "Hello",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["session_id"] == "test-session"
    assert data["reply"] == "Test reply to: Hello"
    assert data["metadata"]["resolution_source"] == "LIVE_INFERENCE"
    assert data["metadata"]["latency_ms"] >= 0


def test_chat_saves_multi_turn_history(client):
    client.post(
        "/chat",
        json={
            "session_id": "history-session",
            "message": "First message",
        },
    )

    client.post(
        "/chat",
        json={
            "session_id": "history-session",
            "message": "Second message",
        },
    )

    response = client.get(
        "/sessions/history-session/messages"
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data["messages"]) == 4
    assert data["messages"][0]["content"] == "First message"
    assert data["messages"][2]["content"] == "Second message"


def test_unknown_session_returns_404(client):
    response = client.get("/sessions/unknown-session/messages")

    assert response.status_code == 404
    assert response.json()["detail"] == "session not found"


def test_empty_message_returns_422(client):
    response = client.post(
        "/chat",
        json={
            "session_id": "test-session",
            "message": "   ",
        },
    )

    assert response.status_code == 422


def test_message_over_4000_characters_returns_422(client):
    response = client.post(
        "/chat",
        json={
            "session_id": "test-session",
            "message": "a" * 4001,
        },
    )

    assert response.status_code == 422


def test_all_providers_unavailable_returns_503(client):
    response = client.post(
        "/chat",
        headers={"X-Simulate-Failure": "*=429"},
        json={
            "session_id": "failure-session",
            "message": "Test failure",
        },
    )

    assert response.status_code == 503
    assert response.json()["detail"] == "all providers unavailable"

    history = client.get(
        "/sessions/failure-session/messages"
    )

    assert history.status_code == 200
    assert history.json()["messages"] == []


def test_custom_system_prompt_is_saved(client):
    response = client.post(
        "/chat",
        json={
            "session_id": "prompt-session",
            "message": "Hello",
            "system_prompt": "Answer in simple English.",
        },
    )

    assert response.status_code == 200

    session = main.get_session("prompt-session")

    assert session["system_prompt"] == "Answer in simple English."
