from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class MemoryCreate(BaseModel):
    content: str = Field(min_length=1, max_length=4000)
    category: str = Field(default="general", min_length=1, max_length=100)


class MemoryItem(MemoryCreate):
    id: int
    created_at: datetime
    updated_at: datetime


class ConversationItem(BaseModel):
    id: int
    role: Literal["user", "assistant", "system"]
    content: str
    created_at: datetime


class ProjectCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    description: str = Field(default="", max_length=4000)
    status: str = Field(default="active", min_length=1, max_length=50)


class ProjectItem(ProjectCreate):
    id: int
    created_at: datetime
    updated_at: datetime


class GoalCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str = Field(default="", max_length=4000)
    status: str = Field(default="active", min_length=1, max_length=50)
    target_date: datetime | None = None


class GoalItem(GoalCreate):
    id: int
    created_at: datetime
    updated_at: datetime


class ReminderCreate(BaseModel):
    title: str = Field(min_length=1, max_length=500)
    due_at: datetime | None = None
    status: str = Field(default="pending", min_length=1, max_length=50)


class ReminderItem(ReminderCreate):
    id: int
    created_at: datetime
    updated_at: datetime


class DeleteResponse(BaseModel):
    deleted: bool
    id: int
