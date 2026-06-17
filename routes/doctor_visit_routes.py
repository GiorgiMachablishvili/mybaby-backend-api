import uuid
from datetime import timezone
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from auth import get_current_user
import models
import schemas

router = APIRouter(prefix="/doctor-visit", tags=["DoctorVisit"])


def _visit_response(v: models.DoctorVisitRecord) -> schemas.DoctorVisitResponse:
    return schemas.DoctorVisitResponse(
        id=str(v.id),
        doctor_name=v.doctor_name or "",
        specialty=v.specialty or "",
        clinic=v.clinic or "",
        visit_date=v.visit_date,
        visit_type=v.visit_type or "WELL-CHECK",
        visit_title=v.visit_title,
        notes=v.notes or "",
        weight_kg=v.weight_kg,
        height_cm=v.height_cm,
        prescriptions=v.prescriptions or "",
        is_completed=v.is_completed or False
    )


def _reminder_response(r: models.VisitReminderRecord) -> schemas.VisitReminderResponse:
    return schemas.VisitReminderResponse(
        id=str(r.id),
        visit_day_timestamp=r.visit_day_timestamp,
        note=r.note or "",
        notify_days_before=r.notify_days_before or "",
        kind_raw=r.kind_raw or "doctorVisit",
        hour=r.hour,
        minute=r.minute
    )


# ── Doctor Visits ─────────────────────────────────────────────────────────────

@router.post("/visit", response_model=schemas.DoctorVisitResponse)
def upsert_visit(
    body: schemas.DoctorVisitCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upsert a doctor visit by UUID."""
    vid = uuid.UUID(body.id) if body.id else uuid.uuid4()
    existing = db.query(models.DoctorVisitRecord).filter_by(id=vid, user_id=current_user.id).first()
    if existing:
        existing.doctor_name  = body.doctor_name or ""
        existing.specialty    = body.specialty or ""
        existing.clinic       = body.clinic or ""
        existing.visit_date   = body.visit_date
        existing.visit_type   = body.visit_type or "WELL-CHECK"
        existing.visit_title  = body.visit_title
        existing.notes        = body.notes or ""
        existing.weight_kg    = body.weight_kg
        existing.height_cm    = body.height_cm
        existing.prescriptions = body.prescriptions or ""
        existing.is_completed = body.is_completed or False
        db.commit()
        return _visit_response(existing)
    record = models.DoctorVisitRecord(
        id=vid, user_id=current_user.id,
        doctor_name=body.doctor_name or "",
        specialty=body.specialty or "",
        clinic=body.clinic or "",
        visit_date=body.visit_date,
        visit_type=body.visit_type or "WELL-CHECK",
        visit_title=body.visit_title,
        notes=body.notes or "",
        weight_kg=body.weight_kg,
        height_cm=body.height_cm,
        prescriptions=body.prescriptions or "",
        is_completed=body.is_completed or False
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return _visit_response(record)


@router.get("/visits", response_model=list[schemas.DoctorVisitResponse])
def get_visits(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all doctor visits for the logged-in user."""
    records = db.query(models.DoctorVisitRecord).filter_by(user_id=current_user.id).all()
    return [_visit_response(v) for v in records]


@router.delete("/visit/{visit_id}", status_code=204)
def delete_visit(
    visit_id: str,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a doctor visit by UUID."""
    vid = uuid.UUID(visit_id)
    record = db.query(models.DoctorVisitRecord).filter_by(id=vid, user_id=current_user.id).first()
    if record:
        db.delete(record)
        db.commit()


# ── Visit Reminders ───────────────────────────────────────────────────────────

@router.post("/reminder", response_model=schemas.VisitReminderResponse)
def upsert_reminder(
    body: schemas.VisitReminderCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upsert a visit reminder by UUID."""
    rid = uuid.UUID(body.id) if body.id else uuid.uuid4()
    existing = db.query(models.VisitReminderRecord).filter_by(id=rid, user_id=current_user.id).first()
    if existing:
        existing.visit_day_timestamp = body.visit_day_timestamp
        existing.note                = body.note or ""
        existing.notify_days_before  = body.notify_days_before or ""
        existing.kind_raw            = body.kind_raw or "doctorVisit"
        existing.hour                = body.hour
        existing.minute              = body.minute
        db.commit()
        return _reminder_response(existing)
    record = models.VisitReminderRecord(
        id=rid, user_id=current_user.id,
        visit_day_timestamp=body.visit_day_timestamp,
        note=body.note or "",
        notify_days_before=body.notify_days_before or "",
        kind_raw=body.kind_raw or "doctorVisit",
        hour=body.hour,
        minute=body.minute
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return _reminder_response(record)


@router.get("/reminders", response_model=list[schemas.VisitReminderResponse])
def get_reminders(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all visit reminders for the logged-in user."""
    records = db.query(models.VisitReminderRecord).filter_by(user_id=current_user.id).all()
    return [_reminder_response(r) for r in records]


@router.delete("/reminder/{reminder_id}", status_code=204)
def delete_reminder(
    reminder_id: str,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a visit reminder by UUID."""
    rid = uuid.UUID(reminder_id)
    record = db.query(models.VisitReminderRecord).filter_by(id=rid, user_id=current_user.id).first()
    if record:
        db.delete(record)
        db.commit()
