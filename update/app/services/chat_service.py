from __future__ import annotations

from datetime import datetime

from app.core.config import settings
from app.services.command_service import execute_natural_command
from app.services.storage_service import list_conversations, list_memories


def _recent_context() -> str:
    memories = list_memories(limit=12)
    conversations = list_conversations(limit=14)

    memory_text = "\n".join(
        f"- [{item.get('category', 'general')}] {item.get('content', '')}"
        for item in reversed(memories)
        if item.get("content")
    )
    conversation_text = "\n".join(
        f"{item.get('role', 'user')}: {item.get('content', '')}"
        for item in conversations
        if item.get("content")
    )

    return (
        "Known personal memory:\n"
        f"{memory_text or '- No saved memories yet.'}\n\n"
        "Recent conversation:\n"
        f"{conversation_text or '- No earlier conversation.'}"
    )


def _cloud_ai_reply(message: str) -> str | None:
    if not settings.openai_api_key:
        return None

    try:
        from openai import OpenAI

        client = OpenAI(api_key=settings.openai_api_key)
        context = _recent_context()
        response = client.responses.create(
            model=settings.openai_model,
            store=False,
            instructions=(
                "You are Jarvis, Chinna's direct, practical personal AI assistant. "
                "Address him as Chinna when natural. Help with SAP EWM, Excel/VBA, "
                "career growth, freelancing, schedules, purchases, travel, and personal "
                "productivity. Use the supplied memories and recent conversation when "
                "relevant. Never claim a Windows action succeeded when the laptop connector "
                "is offline. Keep spoken answers clear and usually under 120 words."
            ),
            input=f"{context}\n\nCurrent user message:\n{message}",
        )
        text = (response.output_text or "").strip()
        return text or "I did not receive a usable AI response. Please try again."
    except Exception as exc:
        # Do not expose API keys or full provider errors to the browser.
        error_name = type(exc).__name__
        return f"The AI service is temporarily unavailable ({error_name}). Please try again."


def generate_reply(message: str) -> str:
    text = message.strip()
    lower = text.lower()

    if not settings.cloud_mode:
        action = execute_natural_command(text)
        if action is not None:
            if action.data and "matches" in action.data:
                matches = action.data.get("matches", [])
                if matches:
                    return action.message + "\n" + "\n".join(
                        f"• {item}" for item in matches[:10]
                    )
            return action.message

    if lower in {"hi", "hello", "hey", "hello jarvis", "hi jarvis", "hey jarvis"}:
        return f"Hello {settings.user_name}. Jarvis is online and ready."

    if lower in {"time", "what time is it", "tell me the time"}:
        return f"The current server time is {datetime.now().strftime('%I:%M %p')}."

    if settings.cloud_mode and lower.startswith(("open ", "launch ", "start ", "lock ")):
        return (
            "That action needs the Windows connector. Your cloud Jarvis is online, "
            "but the laptop connector must also be running for PC control."
        )

    ai_reply = _cloud_ai_reply(text)
    if ai_reply:
        return ai_reply

    return (
        "Jarvis voice is online, but the AI brain is not connected yet. "
        "Add OPENAI_API_KEY to the Render environment and redeploy."
    )
