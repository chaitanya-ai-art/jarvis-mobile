from __future__ import annotations

import json
import os
import secrets
from dataclasses import dataclass
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CONFIG_DIR = PROJECT_ROOT / "config"
CONFIG_FILE = CONFIG_DIR / "settings.json"
DATA_DIR = PROJECT_ROOT / "data"
LOG_DIR = PROJECT_ROOT / "logs"
DATABASE_FILE = DATA_DIR / "jarvis.db"

DEFAULT_CONFIG: dict[str, Any] = {
    "assistant_name": "Jarvis",
    "user_name": "Chinna",
    "version": "8.1.0-voice-ai",
    "host": "0.0.0.0",
    "port": 8765,
    "debug": False,
    "log_level": "INFO",
    "auth_token": "",
    "openai_model": "gpt-5-mini",
}


@dataclass(frozen=True)
class Settings:
    assistant_name: str
    user_name: str
    version: str
    host: str
    port: int
    debug: bool
    log_level: str
    auth_token: str
    cloud_mode: bool
    openai_api_key: str
    openai_model: str


def _env_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _ensure_directories() -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    LOG_DIR.mkdir(parents=True, exist_ok=True)


def _load_raw_config() -> dict[str, Any]:
    _ensure_directories()

    if not CONFIG_FILE.exists():
        initial = dict(DEFAULT_CONFIG)
        initial["auth_token"] = secrets.token_urlsafe(24)
        try:
            CONFIG_FILE.write_text(json.dumps(initial, indent=2), encoding="utf-8")
        except OSError:
            pass
        return initial

    try:
        loaded = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        loaded = {}

    merged = dict(DEFAULT_CONFIG)
    merged.update(loaded if isinstance(loaded, dict) else {})
    merged["version"] = DEFAULT_CONFIG["version"]

    if not str(merged.get("auth_token", "")).strip():
        merged["auth_token"] = secrets.token_urlsafe(24)

    try:
        CONFIG_FILE.write_text(json.dumps(merged, indent=2), encoding="utf-8")
    except OSError:
        pass

    return merged


def load_settings() -> Settings:
    raw = _load_raw_config()
    cloud_mode = _env_bool("CLOUD_MODE") or _env_bool("RENDER")

    auth_token = os.getenv("AUTH_TOKEN", "").strip() or str(raw["auth_token"])

    return Settings(
        assistant_name=os.getenv("ASSISTANT_NAME", str(raw["assistant_name"])),
        user_name=os.getenv("USER_NAME", str(raw["user_name"])),
        version=str(raw["version"]),
        host=os.getenv("HOST", "0.0.0.0" if cloud_mode else str(raw["host"])),
        port=int(os.getenv("PORT", str(raw["port"]))),
        debug=_env_bool("DEBUG", bool(raw["debug"])),
        log_level=os.getenv("LOG_LEVEL", str(raw["log_level"])),
        auth_token=auth_token,
        cloud_mode=cloud_mode,
        openai_api_key=os.getenv("OPENAI_API_KEY", "").strip(),
        openai_model=os.getenv(
            "OPENAI_MODEL",
            str(raw.get("openai_model", DEFAULT_CONFIG["openai_model"])),
        ).strip(),
    )


settings = load_settings()
