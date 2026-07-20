from __future__ import annotations

from typing import Literal

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from app.agents.windows_agent import windows_agent
from app.core.security import require_token
from app.services.command_service import execute_natural_command

router = APIRouter(prefix="/windows", tags=["windows"], dependencies=[Depends(require_token)])


class WindowsActionRequest(BaseModel):
    action: Literal["open_app", "open_folder", "find_file", "system_info", "lock_pc", "recent_actions"]
    argument: str = Field(default="", max_length=260)


class NaturalCommandRequest(BaseModel):
    command: str = Field(min_length=1, max_length=500)


@router.get("/capabilities")
async def capabilities() -> dict[str, object]:
    return {
        "apps": sorted(windows_agent.APP_COMMANDS),
        "folders": sorted(windows_agent.FOLDERS),
        "actions": ["open_app", "open_folder", "find_file", "system_info", "lock_pc", "recent_actions"],
    }


@router.post("/action")
async def run_action(payload: WindowsActionRequest) -> dict[str, object]:
    return windows_agent.execute(payload.action, payload.argument).to_dict()


@router.post("/command")
async def run_natural_command(payload: NaturalCommandRequest) -> dict[str, object]:
    result = execute_natural_command(payload.command)
    if result is None:
        return {"ok": False, "action": "unknown", "message": "No approved Windows command was recognized.", "data": None}
    return result.to_dict()


@router.get("/actions")
async def recent_actions() -> dict[str, object]:
    return {"items": windows_agent.recent_actions()}
