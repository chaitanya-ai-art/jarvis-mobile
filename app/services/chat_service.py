from __future__ import annotations

from datetime import datetime

from app.core.config import settings
from app.services.command_service import execute_natural_command


def generate_reply(message: str) -> str:
    text = message.strip()
    lower = text.lower()

    action = execute_natural_command(text)
    if action is not None:
        if action.data and "matches" in action.data:
            matches = action.data.get("matches", [])
            if matches:
                return action.message + "\n" + "\n".join(f"• {item}" for item in matches[:10])
        return action.message

    if lower in {"hi", "hello", "hey", "hello jarvis", "hi jarvis"}:
        return f"Hello {settings.user_name}. Jarvis Core is online."
    if "time" in lower:
        return f"The current server time is {datetime.now().strftime('%I:%M %p')}."
    if "status" in lower:
        return "Jarvis Windows Automation is online. Say open Excel, open Downloads, find a file, or system info."
    return (
        f"I received your message: {text}. "
        "Try an approved command such as open Excel, open Downloads, find report.xlsx, or system info."
    )
