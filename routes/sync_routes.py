import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from auth import get_current_user
import models
import schemas

router = APIRouter(prefix="/sync", tags=["Sync"])


def _to_uuid(id_str: str | None) -> uuid.UUID:
    try:
        return uuid.UUID(id_str) if id_str else uuid.uuid4()
    except ValueError:
        return uuid.uuid4()


@router.post("", response_model=schemas.SyncResponse)
def sync(
    body: schemas.SyncRequest,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload local data → server saves anything it doesn't have yet.
    Returns ALL data for this user so the iOS app can update its local store.
    """
    uid = current_user.id

    # ── Sleep ────────────────────────────────────────────────────────────────
    for s in body.sleep_sessions:
        sid = _to_uuid(s.id)
        if not db.query(models.SleepSession).filter_by(id=sid, user_id=uid).first():
            db.add(models.SleepSession(id=sid, user_id=uid, start=s.start, end=s.end))

    # ── Feeding ──────────────────────────────────────────────────────────────
    for f in body.feeding_logs:
        fid = _to_uuid(f.id)
        if not db.query(models.FeedingLog).filter_by(id=fid, user_id=uid).first():
            db.add(models.FeedingLog(
                id=fid, user_id=uid,
                type_raw=f.type_raw, volume_text=f.volume_text,
                notes_text=f.notes_text, time_text=f.time_text,
                date_text=f.date_text, saved_at_epoch=f.saved_at_epoch
            ))

    # ── Diaper ───────────────────────────────────────────────────────────────
    for d in body.diaper_logs:
        did = _to_uuid(d.id)
        if not db.query(models.DiaperLog).filter_by(id=did, user_id=uid).first():
            db.add(models.DiaperLog(
                id=did, user_id=uid,
                type_raw=d.type_raw, note=d.note, date=d.date
            ))

    db.commit()
    return _build_response(uid, db)


@router.get("", response_model=schemas.SyncResponse)
def get_all(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Download all data for the logged-in user."""
    return _build_response(current_user.id, db)


def _build_response(uid, db: Session) -> schemas.SyncResponse:
    sleep = db.query(models.SleepSession).filter_by(user_id=uid).all()
    feeds = db.query(models.FeedingLog).filter_by(user_id=uid).all()
    diapers = db.query(models.DiaperLog).filter_by(user_id=uid).all()

    return schemas.SyncResponse(
        sleep_sessions=[
            schemas.SleepSessionResponse(id=str(s.id), start=s.start, end=s.end)
            for s in sleep
        ],
        feeding_logs=[
            schemas.FeedingLogResponse(
                id=str(f.id), type_raw=f.type_raw,
                volume_text=f.volume_text, notes_text=f.notes_text,
                time_text=f.time_text, date_text=f.date_text,
                saved_at_epoch=f.saved_at_epoch
            ) for f in feeds
        ],
        diaper_logs=[
            schemas.DiaperLogResponse(
                id=str(d.id), type_raw=d.type_raw,
                note=d.note, date=d.date
            ) for d in diapers
        ]
    )
