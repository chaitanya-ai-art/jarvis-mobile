from fastapi import APIRouter, Depends, HTTPException, status

from app.core.security import require_token
from app.models.storage import DeleteResponse, ProjectCreate, ProjectItem
from app.services.storage_service import create_project, delete_project, list_projects

router = APIRouter(prefix="/projects", tags=["projects"], dependencies=[Depends(require_token)])


@router.get("", response_model=list[ProjectItem])
def get_projects():
    return list_projects()


@router.post("", response_model=ProjectItem, status_code=status.HTTP_201_CREATED)
def add_project(payload: ProjectCreate):
    return create_project(payload.name, payload.description, payload.status)


@router.delete("/{item_id}", response_model=DeleteResponse)
def remove_project(item_id: int):
    if not delete_project(item_id):
        raise HTTPException(status_code=404, detail="Project not found")
    return DeleteResponse(deleted=True, id=item_id)
