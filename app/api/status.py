from __future__ import annotations

import platform
import sys
from datetime import datetime, timezone

import psutil
from fastapi import APIRouter, Depends

from app.core.config import settings
from app.core.security import require_token

router = APIRouter(tags=["system"])


@router.get("/status", dependencies=[Depends(require_token)])
async def status() -> dict[str, object]:
    return {
        "status": "online",
        "assistant": settings.assistant_name,
        "version": settings.version,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "cpu_percent": psutil.cpu_percent(interval=0.0),
        "memory_percent": psutil.virtual_memory().percent,
    }
