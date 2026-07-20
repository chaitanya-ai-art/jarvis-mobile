from fastapi.testclient import TestClient

from app.core.config import settings
from app.main import app

client = TestClient(app)


def auth_headers() -> dict[str, str]:
    return {"Authorization": f"Bearer {settings.auth_token}"}


def test_health_is_public() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "online"
    assert response.json()["version"] == "7.4.1"


def test_status_requires_token() -> None:
    response = client.get("/status")
    assert response.status_code == 401


def test_status_with_token() -> None:
    response = client.get("/status", headers=auth_headers())
    assert response.status_code == 200
    assert response.json()["assistant"] == "Jarvis"


def test_chat_with_token() -> None:
    response = client.post(
        "/chat",
        headers=auth_headers(),
        json={"message": "hello"},
    )
    assert response.status_code == 200
    assert "Hello Chinna" in response.json()["reply"]


def test_chat_rejects_blank_message() -> None:
    response = client.post(
        "/chat",
        headers=auth_headers(),
        json={"message": ""},
    )
    assert response.status_code == 422
