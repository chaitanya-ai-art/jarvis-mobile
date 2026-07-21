from __future__ import annotations

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from pydantic import BaseModel, Field

from app.core.security import require_auth
from app.services.cloud_developer import developer_jobs

router = APIRouter(prefix="/developer", tags=["developer"])


class DeveloperRequest(BaseModel):
    instruction: str = Field(min_length=5, max_length=2000)


@router.post("/request", dependencies=[Depends(require_auth)])
async def create_developer_request(
    payload: DeveloperRequest,
    background_tasks: BackgroundTasks,
):
    job = developer_jobs.create(payload.instruction)
    background_tasks.add_task(developer_jobs.run, job.id)
    return job.to_dict()


@router.get("/status/{job_id}", dependencies=[Depends(require_auth)])
async def developer_status(job_id: str):
    job = developer_jobs.get(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Developer job not found")
    return job.to_dict()
