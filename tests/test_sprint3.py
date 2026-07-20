from fastapi.testclient import TestClient

from app.core.config import settings
from app.main import app

client = TestClient(app)
HEADERS = {"Authorization": f"Bearer {settings.auth_token}"}


def test_health_version_is_sprint3():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["version"] == "7.4.1"


def test_mobile_dashboard_is_served():
    response = client.get(f"/mobile?token={settings.auth_token}")
    assert response.status_code == 200
    assert "Voice assistant and Windows control" in response.text


def test_dashboard_summary_is_protected():
    with TestClient(app) as isolated_client:
        assert isolated_client.get("/dashboard/summary").status_code == 401
    response = client.get("/dashboard/summary", headers=HEADERS)
    assert response.status_code == 200
    assert "counts" in response.json()


def test_websocket_rejects_bad_token():
    try:
        with client.websocket_connect("/ws?token=bad-token"):
            raise AssertionError("Bad token should not connect")
    except Exception:
        pass


def test_websocket_chat_roundtrip():
    with client.websocket_connect(f"/ws?token={settings.auth_token}") as websocket:
        connected = websocket.receive_json()
        assert connected["type"] == "connected"
        websocket.send_json({"type": "chat", "message": "hello"})
        reply = websocket.receive_json()
        assert reply["type"] == "chat_reply"
        assert "Hello" in reply["message"]
