from __future__ import annotations

import platform
from datetime import datetime, timezone

import psutil
from fastapi import APIRouter, Depends

from app.core.config import settings
from app.core.security import require_token
from app.services.database import fetch_one
from app.services.realtime import manager

router = APIRouter(tags=["dashboard"], dependencies=[Depends(require_token)])


def _count(table: str, where: str = "") -> int:
    row = fetch_one(f"SELECT COUNT(*) AS total FROM {table} {where}")
    return int(row["total"]) if row else 0


@router.get("/dashboard/summary")
async def dashboard_summary() -> dict[str, object]:
    return {
        "assistant": settings.assistant_name,
        "user": settings.user_name,
        "version": settings.version,
        "status": "online",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "platform": platform.system(),
        "cpu_percent": psutil.cpu_percent(interval=0.0),
        "memory_percent": psutil.virtual_memory().percent,
        "connected_devices": manager.count,
        "counts": {
            "memories": _count("memories"),
            "conversations": _count("conversations"),
            "projects": _count("projects"),
            "goals": _count("goals"),
            "reminders": _count("reminders"),
            "pending_reminders": _count("reminders", "WHERE status = 'pending'"),
        },
    }
