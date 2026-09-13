from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_endpoint() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_chat_uses_mock_provider() -> None:
    response = client.post(
        "/chat",
        json={"message": "How can I prepare for a primary-care appointment?"},
    )

    body = response.json()
    assert response.status_code == 200
    assert body["blocked"] is False
    assert body["escalation_required"] is False
    assert body["safety_notice"]
    assert body["request_id"]


def test_chat_does_not_call_model_for_possible_emergency() -> None:
    response = client.post(
        "/chat",
        json={"message": "I cannot breathe right now"},
    )

    body = response.json()
    assert response.status_code == 200
    assert body["blocked"] is True
    assert body["escalation_required"] is True
    assert "emergency" in body["answer"].lower()


def test_blank_chat_message_is_rejected() -> None:
    response = client.post("/chat", json={"message": "   "})

    assert response.status_code == 422