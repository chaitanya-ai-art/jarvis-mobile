from __future__ import annotations

from datetime import datetime
from typing import Any

from app.services.database import execute, execute_insert, fetch_all, fetch_one, utc_now


def _required(row: dict[str, Any] | None, entity: str, item_id: int) -> dict[str, Any]:
    if row is None:
        raise KeyError(f"{entity} {item_id} not found")
    return row


def create_memory(content: str, category: str) -> dict[str, Any]:
    now = utc_now()
    item_id = execute_insert(
        "INSERT INTO memories(category, content, created_at, updated_at) VALUES (?, ?, ?, ?)",
        (category.strip(), content.strip(), now, now),
    )
    return _required(fetch_one("SELECT * FROM memories WHERE id = ?", (item_id,)), "memory", item_id)


def list_memories(limit: int = 100) -> list[dict[str, Any]]:
    return fetch_all("SELECT * FROM memories ORDER BY id DESC LIMIT ?", (limit,))


def delete_memory(item_id: int) -> bool:
    return execute("DELETE FROM memories WHERE id = ?", (item_id,)) > 0


def add_conversation(role: str, content: str) -> dict[str, Any]:
    now = utc_now()
    item_id = execute_insert(
        "INSERT INTO conversations(role, content, created_at) VALUES (?, ?, ?)",
        (role, content.strip(), now),
    )
    return _required(fetch_one("SELECT * FROM conversations WHERE id = ?", (item_id,)), "conversation", item_id)


def list_conversations(limit: int = 100) -> list[dict[str, Any]]:
    rows = fetch_all(
        "SELECT * FROM conversations ORDER BY id DESC LIMIT ?",
        (limit,),
    )
    rows.reverse()
    return rows


def create_project(name: str, description: str, status: str) -> dict[str, Any]:
    now = utc_now()
    item_id = execute_insert(
        "INSERT INTO projects(name, description, status, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
        (name.strip(), description.strip(), status.strip(), now, now),
    )
    return _required(fetch_one("SELECT * FROM projects WHERE id = ?", (item_id,)), "project", item_id)


def list_projects() -> list[dict[str, Any]]:
    return fetch_all("SELECT * FROM projects ORDER BY id DESC")


def delete_project(item_id: int) -> bool:
    return execute("DELETE FROM projects WHERE id = ?", (item_id,)) > 0


def create_goal(title: str, description: str, status: str, target_date: datetime | None) -> dict[str, Any]:
    now = utc_now()
    target = target_date.isoformat() if target_date else None
    item_id = execute_insert(
        "INSERT INTO goals(title, description, status, target_date, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)",
        (title.strip(), description.strip(), status.strip(), target, now, now),
    )
    return _required(fetch_one("SELECT * FROM goals WHERE id = ?", (item_id,)), "goal", item_id)


def list_goals() -> list[dict[str, Any]]:
    return fetch_all("SELECT * FROM goals ORDER BY id DESC")


def delete_goal(item_id: int) -> bool:
    return execute("DELETE FROM goals WHERE id = ?", (item_id,)) > 0


def create_reminder(title: str, status: str, due_at: datetime | None) -> dict[str, Any]:
    now = utc_now()
    due = due_at.isoformat() if due_at else None
    item_id = execute_insert(
        "INSERT INTO reminders(title, due_at, status, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
        (title.strip(), due, status.strip(), now, now),
    )
    return _required(fetch_one("SELECT * FROM reminders WHERE id = ?", (item_id,)), "reminder", item_id)


def list_reminders() -> list[dict[str, Any]]:
    return fetch_all(
        "SELECT * FROM reminders ORDER BY CASE WHEN due_at IS NULL THEN 1 ELSE 0 END, due_at, id DESC"
    )


def delete_reminder(item_id: int) -> bool:
    return execute("DELETE FROM reminders WHERE id = ?", (item_id,)) > 0
