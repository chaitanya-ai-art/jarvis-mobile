from uuid import uuid4

from fastapi.testclient import TestClient

from app.core.config import settings
from app.main import app

client = TestClient(app)


def headers() -> dict[str, str]:
    return {"Authorization": f"Bearer {settings.auth_token}"}


def test_version_upgraded() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["version"] == "7.4.1"


def test_memory_crud() -> None:
    content = f"memory-{uuid4()}"
    created = client.post("/memory", headers=headers(), json={"content": content, "category": "test"})
    assert created.status_code == 201
    item_id = created.json()["id"]
    listed = client.get("/memory", headers=headers())
    assert any(item["id"] == item_id and item["content"] == content for item in listed.json())
    deleted = client.delete(f"/memory/{item_id}", headers=headers())
    assert deleted.status_code == 200


def test_project_goal_reminder_crud() -> None:
    project = client.post("/projects", headers=headers(), json={"name": f"project-{uuid4()}"})
    assert project.status_code == 201
    assert client.delete(f"/projects/{project.json()['id']}", headers=headers()).status_code == 200

    goal = client.post("/goals", headers=headers(), json={"title": f"goal-{uuid4()}"})
    assert goal.status_code == 201
    assert client.delete(f"/goals/{goal.json()['id']}", headers=headers()).status_code == 200

    reminder = client.post("/reminders", headers=headers(), json={"title": f"reminder-{uuid4()}"})
    assert reminder.status_code == 201
    assert client.delete(f"/reminders/{reminder.json()['id']}", headers=headers()).status_code == 200


def test_chat_is_saved_to_conversation_history() -> None:
    marker = f"chat-{uuid4()}"
    response = client.post("/chat", headers=headers(), json={"message": marker})
    assert response.status_code == 200
    history = client.get("/conversations?limit=20", headers=headers())
    assert history.status_code == 200
    contents = [item["content"] for item in history.json()]
    assert marker in contents
    assert response.json()["reply"] in contents


def test_storage_endpoints_require_token() -> None:
    assert client.get("/memory").status_code == 401
    assert client.get("/projects").status_code == 401
    assert client.get("/goals").status_code == 401
    assert client.get("/reminders").status_code == 401
