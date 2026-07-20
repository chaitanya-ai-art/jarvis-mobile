from fastapi import APIRouter, Depends, Query

from app.core.security import require_token
from app.models.storage import ConversationItem
from app.services.storage_service import list_conversations

router = APIRouter(prefix="/conversations", tags=["conversations"], dependencies=[Depends(require_token)])


@router.get("", response_model=list[ConversationItem])
def get_conversations(limit: int = Query(default=100, ge=1, le=500)):
    return list_conversations(limit)
