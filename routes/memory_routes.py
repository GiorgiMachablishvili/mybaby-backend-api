import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from auth import get_current_user
import models
import schemas

router = APIRouter(prefix="/memory", tags=["Memory"])


def _response(m: models.BabyMemoryRecord) -> schemas.BabyMemoryResponse:
    return schemas.BabyMemoryResponse(
        id=str(m.id),
        title=m.title,
        date=m.date,
        text=m.text or "",
        category=m.category or "memories"
    )


@router.post("", response_model=schemas.BabyMemoryResponse)
def add_memory(
    body: schemas.BabyMemoryCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Save a baby memory (idempotent by UUID)."""
    mid = uuid.UUID(body.id) if body.id else uuid.uuid4()
    existing = db.query(models.BabyMemoryRecord).filter_by(id=mid, user_id=current_user.id).first()
    if existing:
        return _response(existing)
    record = models.BabyMemoryRecord(
        id=mid, user_id=current_user.id,
        title=body.title,
        date=body.date,
        text=body.text or "",
        category=body.category or "memories"
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return _response(record)


@router.get("", response_model=list[schemas.BabyMemoryResponse])
def get_memories(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all baby memories, newest first."""
    records = (
        db.query(models.BabyMemoryRecord)
        .filter_by(user_id=current_user.id)
        .order_by(models.BabyMemoryRecord.date.desc())
        .all()
    )
    return [_response(r) for r in records]


@router.delete("/{memory_id}", status_code=204)
def delete_memory(
    memory_id: str,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a baby memory by UUID."""
    mid = uuid.UUID(memory_id)
    record = db.query(models.BabyMemoryRecord).filter_by(id=mid, user_id=current_user.id).first()
    if record:
        db.delete(record)
        db.commit()
