import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from auth import get_current_user
import models
import schemas

router = APIRouter(prefix="/feeding", tags=["Feeding"])


@router.post("", response_model=schemas.FeedingLogResponse)
def add_feeding(
    body: schemas.FeedingLogCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Save a single feeding entry."""
    fid = uuid.UUID(body.id) if body.id else uuid.uuid4()
    existing = db.query(models.FeedingLog).filter_by(id=fid, user_id=current_user.id).first()
    if existing:
        return schemas.FeedingLogResponse(
            id=str(existing.id),
            type_raw=existing.type_raw,
            volume_text=existing.volume_text,
            notes_text=existing.notes_text,
            time_text=existing.time_text,
            date_text=existing.date_text,
            saved_at_epoch=existing.saved_at_epoch
        )
    entry = models.FeedingLog(
        id=fid,
        user_id=current_user.id,
        type_raw=body.type_raw,
        volume_text=body.volume_text,
        notes_text=body.notes_text,
        time_text=body.time_text,
        date_text=body.date_text,
        saved_at_epoch=body.saved_at_epoch
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return schemas.FeedingLogResponse(
        id=str(entry.id),
        type_raw=entry.type_raw,
        volume_text=entry.volume_text,
        notes_text=entry.notes_text,
        time_text=entry.time_text,
        date_text=entry.date_text,
        saved_at_epoch=entry.saved_at_epoch
    )


@router.get("", response_model=list[schemas.FeedingLogResponse])
def get_feedings(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all feeding entries for the logged-in user, newest first."""
    entries = (
        db.query(models.FeedingLog)
        .filter_by(user_id=current_user.id)
        .order_by(models.FeedingLog.created_at.desc())
        .all()
    )
    return [
        schemas.FeedingLogResponse(
            id=str(e.id),
            type_raw=e.type_raw,
            volume_text=e.volume_text,
            notes_text=e.notes_text,
            time_text=e.time_text,
            date_text=e.date_text,
            saved_at_epoch=e.saved_at_epoch
        )
        for e in entries
    ]
