from fastapi import APIRouter

from app.core.config import settings

router = APIRouter(tags=["system"])


@router.get("/health")
async def health() -> dict[str, str]:
    return {
        "status": "online",
        "version": settings.version,
        "assistant": settings.assistant_name,
    }
