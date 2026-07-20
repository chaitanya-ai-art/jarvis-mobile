from __future__ import annotations

import re
from dataclasses import dataclass

from app.agents.windows_agent import ActionResult, windows_agent


@dataclass(frozen=True)
class ParsedCommand:
    action: str
    argument: str = ""


APP_ALIASES = {
    "google chrome": "chrome",
    "chrome": "chrome",
    "microsoft edge": "edge",
    "edge": "edge",
    "excel": "excel",
    "microsoft excel": "excel",
    "notepad": "notepad",
    "calculator": "calculator",
    "calc": "calculator",
    "vs code": "vscode",
    "visual studio code": "vscode",
    "paint": "paint",
    "settings": "settings",
}
FOLDER_ALIASES = {name: name for name in ("downloads", "documents", "desktop", "pictures", "jarvis")}

_WAKE_PREFIX = re.compile(r"^(?:hey\s+)?jarvis[,:]?\s+", re.IGNORECASE)
_POLITE_PREFIX = re.compile(r"^(?:please\s+|can you\s+|could you\s+|would you\s+)", re.IGNORECASE)
_POLITE_SUFFIX = re.compile(r"(?:\s+please|\s+for me)[.!?]*$", re.IGNORECASE)


def _normalize_message(message: str) -> str:
    text = " ".join(message.strip().split())
    text = _WAKE_PREFIX.sub("", text)
    # Remove up to two polite prefixes, e.g. "Jarvis, can you please open Excel"
    for _ in range(2):
        updated = _POLITE_PREFIX.sub("", text)
        if updated == text:
            break
        text = updated
    text = _POLITE_SUFFIX.sub("", text)
    return text.strip(" .!?\t\r\n").lower()


def parse_windows_command(message: str) -> ParsedCommand | None:
    """Parse only approved, deterministic Windows commands.

    The parser accepts wake-word and polite variants while never forwarding
    arbitrary text to a shell.
    """
    text = _normalize_message(message)
    if not text:
        return None

    if text in {
        "system info", "pc status", "computer status", "windows status",
        "show cpu", "show ram", "show battery", "cpu", "ram", "battery",
    }:
        return ParsedCommand("system_info")
    if text in {"lock pc", "lock computer", "lock my pc"}:
        return ParsedCommand("lock_pc")
    if text in {"show action log", "recent actions", "action history", "show recent actions"}:
        return ParsedCommand("recent_actions")

    match = re.fullmatch(r"(?:open|start|launch)\s+(?:the\s+)?(.+)", text)
    if match:
        target = match.group(1).strip()
        if target in APP_ALIASES:
            return ParsedCommand("open_app", APP_ALIASES[target])
        if target.endswith(" folder"):
            target = target[:-7].strip()
        if target in FOLDER_ALIASES:
            return ParsedCommand("open_folder", FOLDER_ALIASES[target])

    match = re.fullmatch(r"(?:find|search for|locate)\s+(?:the\s+)?(?:file\s+)?(.+)", text)
    if match:
        query = match.group(1).strip()
        if query:
            return ParsedCommand("find_file", query)
    return None


def execute_natural_command(message: str) -> ActionResult | None:
    parsed = parse_windows_command(message)
    if parsed is None:
        return None
    return windows_agent.execute(parsed.action, parsed.argument)
