from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.core.security import require_token
from app.models.storage import DeleteResponse, MemoryCreate, MemoryItem
from app.services.storage_service import create_memory, delete_memory, list_memories

router = APIRouter(prefix="/memory", tags=["memory"], dependencies=[Depends(require_token)])


@router.get("", response_model=list[MemoryItem])
def get_memories(limit: int = Query(default=100, ge=1, le=500)):
    return list_memories(limit)


@router.post("", response_model=MemoryItem, status_code=status.HTTP_201_CREATED)
def add_memory(payload: MemoryCreate):
    return create_memory(payload.content, payload.category)


@router.delete("/{item_id}", response_model=DeleteResponse)
def remove_memory(item_id: int):
    if not delete_memory(item_id):
        raise HTTPException(status_code=404, detail="Memory not found")
    return DeleteResponse(deleted=True, id=item_id)
