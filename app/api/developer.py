from __future__ import annotations

from fastapi import APIRouter, BackgroundTasks, Cookie, Header, HTTPException, Query
from pydantic import BaseModel, Field

from app.core.security import SESSION_COOKIE, is_valid_token
from app.services.cloud_developer import developer_jobs

router = APIRouter(prefix="/developer", tags=["developer"])


class DeveloperRequest(BaseModel):
    instruction: str = Field(min_length=5, max_length=2000)


def verify_developer_auth(
    token: str | None = Query(default=None),
    jarvis_session: str | None = Cookie(
        default=None,
        alias=SESSION_COOKIE,
    ),
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