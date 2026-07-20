from fastapi import APIRouter, Depends, HTTPException, status

from app.core.security import require_token
from app.models.storage import DeleteResponse, GoalCreate, GoalItem
from app.services.storage_service import create_goal, delete_goal, list_goals

router = APIRouter(prefix="/goals", tags=["goals"], dependencies=[Depends(require_token)])


@router.get("", response_model=list[GoalItem])
def get_goals():
    return list_goals()


@router.post("", response_model=GoalItem, status_code=status.HTTP_201_CREATED)
def add_goal(payload: GoalCreate):
    return create_goal(payload.title, payload.description, payload.status, payload.target_date)


@router.delete("/{item_id}", response_model=DeleteResponse)
def remove_goal(item_id: int):
    if not delete_goal(item_id):
        raise HTTPException(status_code=404, detail="Goal not found")
    return DeleteResponse(deleted=True, id=item_id)
