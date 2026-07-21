from fastapi.testclient import TestClient

from app.core.config import settings
from app.core.security import SESSION_COOKIE
from app.main import app


def test_mobile_valid_token_creates_session_cookie() -> None:
    with TestClient(app) as client:
        response = client.get(f"/mobile?token={settings.auth_token}")
        assert response.status_code == 200
        assert SESSION_COOKIE in response.cookies
        assert response.headers.get("cache-control") == "no-store, max-age=0"


def test_dashboard_accepts_session_cookie_without_bearer() -> None:
    with TestClient(app) as client:
        login = client.get(f"/mobile?token={settings.auth_token}")
        assert login.status_code == 200
        response = client.get("/dashboard/summary")
        assert response.status_code == 200


def test_mobile_rejects_invalid_token_without_valid_cookie() -> None:
    with TestClient(app) as client:
        response = client.get("/mobile?token=stale-token")
        assert response.status_code == 401
        assert "login required" in response.text.lower()


def test_websocket_accepts_authenticated_session_cookie() -> None:
    with TestClient(app) as client:
        client.get(f"/mobile?token={settings.auth_token}")
        with client.websocket_connect("/ws") as websocket:
            payload = websocket.receive_json()
            assert payload["type"] == "connected"


def test_websocket_rejects_missing_authentication() -> None:
    with TestClient(app) as client:
        try:
            with client.websocket_connect("/ws"):
                raise AssertionError("Unauthenticated WebSocket should not connect")
        except Exception:
            pass


