import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from auth import get_current_user
import models
import schemas

router = APIRouter(prefix="/diaper", tags=["Diaper"])


@router.post("", response_model=schemas.DiaperLogResponse)
def add_diaper(
    body: schemas.DiaperLogCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Save a single diaper log entry (idempotent by UUID)."""
    lid = uuid.UUID(body.id) if body.id else uuid.uuid4()
    existing = db.query(models.DiaperLog).filter_by(id=lid, user_id=current_user.id).first()
    if existing:
        return schemas.DiaperLogResponse(
            id=str(existing.id), type_raw=existing.type_raw,
            note=existing.note, date=existing.date
        )
    entry = models.DiaperLog(
        id=lid, user_id=current_user.id,
        type_raw=body.type_raw, note=body.note, date=body.date
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return schemas.DiaperLogResponse(
        id=str(entry.id), type_raw=entry.type_raw,
        note=entry.note, date=entry.date
    )


@router.get("", response_model=list[schemas.DiaperLogResponse])
def get_diapers(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all diaper entries for the logged-in user, newest first."""
    entries = (
        db.query(models.DiaperLog)
        .filter_by(user_id=current_user.id)
        .order_by(models.DiaperLog.date.desc())
        .all()
    )
    return [
        schemas.DiaperLogResponse(
            id=str(e.id), type_raw=e.type_raw,
            note=e.note, date=e.date
        )
        for e in entries
    ]
