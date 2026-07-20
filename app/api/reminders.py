from fastapi import APIRouter, Depends, HTTPException, status

from app.core.security import require_token
from app.models.storage import DeleteResponse, ReminderCreate, ReminderItem
from app.services.storage_service import create_reminder, delete_reminder, list_reminders

router = APIRouter(prefix="/reminders", tags=["reminders"], dependencies=[Depends(require_token)])


@router.get("", response_model=list[ReminderItem])
def get_reminders():
    return list_reminders()


@router.post("", response_model=ReminderItem, status_code=status.HTTP_201_CREATED)
def add_reminder(payload: ReminderCreate):
    return create_reminder(payload.title, payload.status, payload.due_at)


@router.delete("/{item_id}", response_model=DeleteResponse)
def remove_reminder(item_id: int):
    if not delete_reminder(item_id):
        raise HTTPException(status_code=404, detail="Reminder not found")
    return DeleteResponse(deleted=True, id=item_id)
