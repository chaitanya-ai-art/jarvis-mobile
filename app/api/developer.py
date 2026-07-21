from __future__ import annotations

import os
import secrets

from fastapi import APIRouter, BackgroundTasks, Cookie, Header, HTTPException, Query
from pydantic import BaseModel, Field

from app.core.security import SESSION_COOKIE, is_valid_token
from app.services.cloud_developer import developer_jobs

router = APIRouter(prefix="/developer", tags=["developer"])


class DeveloperRequest(BaseModel):
    instruction: str = Field(min_length=5, max_length=2000)


class ApprovalRequest(BaseModel):
    approval_pin: str = Field(min_length=4, max_length=128)


def verify_developer_auth(
    token: str | None = Query(default=None),
    jarvis_session: str | None = Cookie(default=None, alias=SESSION_COOKIE),
    authorization: str | None = Header(default=None),
) -> None:
    selected_token = token or jarvis_session

    if authorization and authorization.lower().startswith("bearer "):
        selected_token = authorization[7:].strip()

    if not is_valid_token(selected_token):
        raise HTTPException(
            status_code=401,
            detail="Unauthorized developer request",
        )


def verify_approval_pin(candidate: str) -> None:
    configured = os.getenv("DEVELOPER_APPROVAL_PIN", "").strip()

    if not configured:
        raise HTTPException(
            status_code=503,
            detail="DEVELOPER_APPROVAL_PIN is not configured",
        )

    if not secrets.compare_digest(candidate.strip(), configured):
        raise HTTPException(
            status_code=403,
            detail="Incorrect developer approval PIN",
        )


@router.post("/request")
async def create_developer_request(
    payload: DeveloperRequest,
    background_tasks: BackgroundTasks,
    _: None = verify_developer_auth,
):
    job = developer_jobs.create(payload.instruction)
    background_tasks.add_task(developer_jobs.run, job.id)
    return job.to_dict()


@router.get("/status/{job_id}")
async def developer_status(
    job_id: str,
    _: None = verify_developer_auth,
):
    job = developer_jobs.get(job_id)

    if job is None:
        raise HTTPException(
            status_code=404,
            detail="Developer job not found",
        )

    return job.to_dict()


@router.post("/approve/{job_id}")
async def approve_developer_job(
    job_id: str,
    payload: ApprovalRequest,
    background_tasks: BackgroundTasks,
    _: None = verify_developer_auth,
):
    verify_approval_pin(payload.approval_pin)

    job = developer_jobs.get(job_id)
    if job is None:
        raise HTTPException(
            status_code=404,
            detail="Developer job not found",
        )

    if job.status != "ready" or job.pull_request_number is None:
        raise HTTPException(
            status_code=409,
            detail="Developer job is not ready for approval",
        )

    background_tasks.add_task(developer_jobs.approve, job.id)
    return {
        "id": job.id,
        "status": "approval_queued",
        "message": "Approval accepted. Jarvis is merging the reviewed pull request.",
    }
