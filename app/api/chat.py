from fastapi import APIRouter, Depends

from app.core.config import settings
from app.core.security import require_token
from app.models.chat import ChatRequest, ChatResponse
from app.services.chat_service import generate_reply
from app.services.storage_service import add_conversation

router = APIRouter(tags=["chat"])


@router.post("/chat", response_model=ChatResponse, dependencies=[Depends(require_token)])
async def chat(payload: ChatRequest) -> ChatResponse:
    add_conversation("user", payload.message)
    reply = generate_reply(payload.message)
    add_conversation("assistant", reply)
    return ChatResponse(
        reply=reply,
        assistant=settings.assistant_name,
        version=settings.version,
    )
