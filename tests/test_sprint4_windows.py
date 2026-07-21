from __future__ import annotations

from unittest.mock import patch

from fastapi.testclient import TestClient

from app.agents.windows_agent import windows_agent
from app.core.config import settings
from app.main import app
from app.services.command_service import parse_windows_command

client = TestClient(app)
HEADERS = {"Authorization": f"Bearer {settings.auth_token}"}


def test_parser_recognizes_safe_commands() -> None:
    assert parse_windows_command("open Excel").action == "open_app"
    assert parse_windows_command("open downloads folder").action == "open_folder"
    assert parse_windows_command("find report.xlsx").action == "find_file"
    assert parse_windows_command("delete c drive") is None


def test_capabilities_requires_token() -> None:
    assert client.get("/windows/capabilities").status_code == 401
    response = client.get("/windows/capabilities", headers=HEADERS)
    assert response.status_code == 200
    assert "excel" in response.json()["apps"]


def test_unknown_action_is_blocked() -> None:
    result = windows_agent.execute("run_shell", "format c:")
    assert result.ok is False
    assert "not approved" in result.message


def test_natural_command_endpoint_system_info() -> None:
    response = client.post("/windows/command", headers=HEADERS, json={"command": "system info"})
    assert response.status_code == 200
    assert response.json()["ok"] is True
    assert response.json()["action"] == "system_info"


def test_open_app_uses_allow_list() -> None:
    with patch("app.agents.windows_agent.platform.system", return_value="Windows"), patch(
        "app.agents.windows_agent.subprocess.Popen"
    ) as popen:
        result = windows_agent.open_app("excel")
    assert result.ok is True
    popen.assert_called_once()

