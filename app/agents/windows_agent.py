from __future__ import annotations

import json
import os
import platform
import subprocess
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

import psutil

from app.core.config import LOG_DIR

ACTION_DIR = LOG_DIR / "actions"
ACTION_LOG = ACTION_DIR / "actions.jsonl"


@dataclass(frozen=True)
class ActionResult:
    ok: bool
    action: str
    message: str
    data: dict[str, object] | None = None

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


class WindowsActionAgent:
    """Executes only approved Windows actions. It never runs arbitrary shell text."""

    APP_COMMANDS: dict[str, list[str]] = {
        "chrome": ["cmd", "/c", "start", "", "chrome"],
        "edge": ["cmd", "/c", "start", "", "msedge"],
        "excel": ["cmd", "/c", "start", "", "excel"],
        "notepad": ["notepad.exe"],
        "calculator": ["calc.exe"],
        "vscode": ["cmd", "/c", "start", "", "code"],
        "paint": ["mspaint.exe"],
        "settings": ["cmd", "/c", "start", "", "ms-settings:"],
    }

    FOLDERS: dict[str, Path] = {
        "downloads": Path.home() / "Downloads",
        "documents": Path.home() / "Documents",
        "desktop": Path.home() / "Desktop",
        "pictures": Path.home() / "Pictures",
        "jarvis": Path("D:/Jarvis"),
    }

    SEARCH_ROOTS: tuple[Path, ...] = (
        Path.home() / "Downloads",
        Path.home() / "Documents",
        Path.home() / "Desktop",
        Path("D:/Jarvis"),
    )

    def __init__(self) -> None:
        ACTION_DIR.mkdir(parents=True, exist_ok=True)

    def execute(self, action: str, argument: str = "") -> ActionResult:
        normalized = action.strip().lower().replace(" ", "_")
        try:
            if normalized == "open_app":
                result = self.open_app(argument)
            elif normalized == "open_folder":
                result = self.open_folder(argument)
            elif normalized == "find_file":
                result = self.find_file(argument)
            elif normalized == "system_info":
                result = self.system_info()
            elif normalized == "lock_pc":
                result = self.lock_pc()
            elif normalized == "recent_actions":
                result = ActionResult(True, normalized, "Recent actions loaded.", {"items": self.recent_actions()})
            else:
                result = ActionResult(False, normalized, "That Windows action is not approved.")
        except Exception as exc:  # defensive boundary for OS failures
            result = ActionResult(False, normalized, f"Windows action failed: {exc}")
        self._log(result, argument)
        return result

    def open_app(self, app_name: str) -> ActionResult:
        key = self._normalize_name(app_name)
        command = self.APP_COMMANDS.get(key)
        if not command:
            allowed = ", ".join(sorted(self.APP_COMMANDS))
            return ActionResult(False, "open_app", f"App not approved. Allowed apps: {allowed}.")
        if platform.system() != "Windows":
            return ActionResult(False, "open_app", "App launching is available only on Windows.")
        subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return ActionResult(True, "open_app", f"Opening {key}.", {"app": key})

    def open_folder(self, folder_name: str) -> ActionResult:
        key = self._normalize_name(folder_name)
        path = self.FOLDERS.get(key)
        if not path:
            allowed = ", ".join(sorted(self.FOLDERS))
            return ActionResult(False, "open_folder", f"Folder not approved. Allowed folders: {allowed}.")
        if not path.exists():
            return ActionResult(False, "open_folder", f"Folder does not exist: {path}")
        if platform.system() != "Windows":
            return ActionResult(False, "open_folder", "Folder opening is available only on Windows.")
        os.startfile(str(path))  # type: ignore[attr-defined]
        return ActionResult(True, "open_folder", f"Opening {key} folder.", {"path": str(path)})

    def find_file(self, query: str, limit: int = 20) -> ActionResult:
        needle = query.strip().lower()
        if len(needle) < 2:
            return ActionResult(False, "find_file", "Enter at least two characters to search.")
        matches: list[str] = []
        for base in self.SEARCH_ROOTS:
            if not base.exists():
                continue
            try:
                for path in base.rglob("*"):
                    if path.is_file() and needle in path.name.lower():
                        matches.append(str(path))
                        if len(matches) >= limit:
                            break
            except (PermissionError, OSError):
                continue
            if len(matches) >= limit:
                break
        if not matches:
            return ActionResult(True, "find_file", f"No files found for '{query}'.", {"matches": []})
        return ActionResult(True, "find_file", f"Found {len(matches)} matching file(s).", {"matches": matches})

    def system_info(self) -> ActionResult:
        battery = psutil.sensors_battery()
        disk = psutil.disk_usage(Path.home().anchor or "C:/")
        data: dict[str, object] = {
            "computer": platform.node(),
            "platform": platform.platform(),
            "cpu_percent": psutil.cpu_percent(interval=0.0),
            "ram_percent": psutil.virtual_memory().percent,
            "disk_percent": disk.percent,
            "battery_percent": battery.percent if battery else None,
            "battery_plugged": battery.power_plugged if battery else None,
        }
        message = (
            f"CPU {data['cpu_percent']}%, RAM {data['ram_percent']}%, "
            f"disk {data['disk_percent']}%."
        )
        if data["battery_percent"] is not None:
            message += f" Battery {data['battery_percent']}%."
        return ActionResult(True, "system_info", message, data)

    def lock_pc(self) -> ActionResult:
        if platform.system() != "Windows":
            return ActionResult(False, "lock_pc", "PC locking is available only on Windows.")
        subprocess.Popen(["rundll32.exe", "user32.dll,LockWorkStation"])
        return ActionResult(True, "lock_pc", "Locking the PC.")

    def recent_actions(self, limit: int = 20) -> list[dict[str, object]]:
        if not ACTION_LOG.exists():
            return []
        lines = ACTION_LOG.read_text(encoding="utf-8", errors="replace").splitlines()[-limit:]
        items: list[dict[str, object]] = []
        for line in lines:
            try:
                item = json.loads(line)
                if isinstance(item, dict):
                    items.append(item)
            except json.JSONDecodeError:
                continue
        return list(reversed(items))

    @staticmethod
    def _normalize_name(value: str) -> str:
        return value.strip().lower().replace(" ", "").replace("_", "")

    def _log(self, result: ActionResult, argument: str) -> None:
        entry = {
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "action": result.action,
            "argument": argument,
            "ok": result.ok,
            "message": result.message,
        }
        with ACTION_LOG.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(entry, ensure_ascii=False) + "\n")


windows_agent = WindowsActionAgent()
