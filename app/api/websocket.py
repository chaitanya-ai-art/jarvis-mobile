from __future__ import annotations

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, status

from app.core.security import SESSION_COOKIE, is_valid_token
from app.core.config import settings
from app.services.chat_service import generate_reply
from app.services.realtime import manager
from app.services.storage_service import add_conversation

router = APIRouter(tags=["realtime"])


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket) -> None:
    query_token = websocket.query_params.get("token")
    cookie_token = websocket.cookies.get(SESSION_COOKIE)
    if not (is_valid_token(query_token) or is_valid_token(cookie_token)):
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    await manager.connect(websocket)
    await manager.send_json(
        websocket,
        {
            "type": "connected",
            "message": f"{settings.assistant_name} is connected.",
            "version": settings.version,
        },
    )

    try:
        while True:
            payload = await websocket.receive_json()
            event_type = str(payload.get("type", "chat"))

            if event_type == "ping":
                await manager.send_json(websocket, {"type": "pong"})
                continue

            if event_type != "chat":
                await manager.send_json(
                    websocket,
                    {"type": "error", "message": "Unsupported event type."},
                )
                continue

            message = str(payload.get("message", "")).strip()
            if not message:
                await manager.send_json(
                    websocket,
                    {"type": "error", "message": "Message cannot be empty."},
                )
                continue

            add_conversation("user", message)
            reply = generate_reply(message)
            add_conversation("assistant", reply)
            await manager.send_json(
                websocket,
                {
                    "type": "chat_reply",
                    "message": reply,
                    "assistant": settings.assistant_name,
                },
            )
            await manager.broadcast(
                {
                    "type": "activity",
                    "message": "Conversation saved",
                }
            )
    except WebSocketDisconnect:
        await manager.disconnect(websocket)
    except Exception:
        await manager.disconnect(websocket)
        try:
            await websocket.close(code=status.WS_1011_INTERNAL_ERROR)
        except Exception:
            pass
