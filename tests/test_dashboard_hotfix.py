from fastapi.testclient import TestClient

from app.core.config import settings
from app.main import app


def test_root_with_token_redirects_to_mobile() -> None:
    client = TestClient(app, follow_redirects=False)
    response = client.get(f"/?token={settings.auth_token}")
    assert response.status_code == 307
    assert response.headers["location"] == f"/mobile?token={settings.auth_token}"


def test_mobile_dashboard_is_html() -> None:
    client = TestClient(app)
    response = client.get(f"/mobile?token={settings.auth_token}")
    assert response.status_code == 200
    assert "JARVIS" in response.text
    assert "Live chat" in response.text


def test_health_reports_hotfix_version() -> None:
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["version"] == "7.4.1"
