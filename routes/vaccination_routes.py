import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from auth import get_current_user
import models
import schemas

router = APIRouter(prefix="/vaccination", tags=["Vaccination"])


def _vaccine_response(v: models.VaccineRecord) -> schemas.VaccineRecordResponse:
    return schemas.VaccineRecordResponse(
        id=str(v.id), name=v.name, full_name=v.full_name,
        age_range=v.age_range or "",
        due_date_timestamp=v.due_date_timestamp,
        scheduled_timestamp=v.scheduled_timestamp,
        scheduled_hour=v.scheduled_hour,
        scheduled_minute=v.scheduled_minute,
        completed_timestamp=v.completed_timestamp,
        dose_number=v.dose_number,
        total_doses=v.total_doses,
        doctor_name=v.doctor_name,
        notes=v.notes or ""
    )


def _reminder_response(r: models.VaccinationReminderRecord) -> schemas.VaccinationReminderResponse:
    return schemas.VaccinationReminderResponse(
        id=str(r.id),
        day_timestamp=r.day_timestamp,
        hour=r.hour,
        minute=r.minute,
        note=r.note or "",
        is_enabled=r.is_enabled,
        notify_days_before=r.notify_days_before or ""
    )


# ── Vaccines ──────────────────────────────────────────────────────────────────

@router.post("/vaccine", response_model=schemas.VaccineRecordResponse)
def upsert_vaccine(
    body: schemas.VaccineRecordCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upsert a vaccine record by UUID."""
    vid = uuid.UUID(body.id) if body.id else uuid.uuid4()
    existing = db.query(models.VaccineRecord).filter_by(id=vid, user_id=current_user.id).first()
    if existing:
        existing.name                = body.name
        existing.full_name           = body.full_name
        existing.age_range           = body.age_range or ""
        existing.due_date_timestamp  = body.due_date_timestamp
        existing.scheduled_timestamp = body.scheduled_timestamp
        existing.scheduled_hour      = body.scheduled_hour
        existing.scheduled_minute    = body.scheduled_minute
        existing.completed_timestamp = body.completed_timestamp
        existing.dose_number         = body.dose_number
        existing.total_doses         = body.total_doses
        existing.doctor_name         = body.doctor_name
        existing.notes               = body.notes or ""
        db.commit()
        return _vaccine_response(existing)
    record = models.VaccineRecord(
        id=vid, user_id=current_user.id,
        name=body.name, full_name=body.full_name,
        age_range=body.age_range or "",
        due_date_timestamp=body.due_date_timestamp,
        scheduled_timestamp=body.scheduled_timestamp,
        scheduled_hour=body.scheduled_hour,
        scheduled_minute=body.scheduled_minute,
        completed_timestamp=body.completed_timestamp,
        dose_number=body.dose_number,
        total_doses=body.total_doses,
        doctor_name=body.doctor_name,
        notes=body.notes or ""
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return _vaccine_response(record)


@router.get("/vaccines", response_model=list[schemas.VaccineRecordResponse])
def get_vaccines(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all vaccine records for the logged-in user."""
    records = db.query(models.VaccineRecord).filter_by(user_id=current_user.id).all()
    return [_vaccine_response(v) for v in records]


@router.delete("/vaccine/{vaccine_id}", status_code=204)
def delete_vaccine(
    vaccine_id: str,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a vaccine record by UUID."""
    vid = uuid.UUID(vaccine_id)
    record = db.query(models.VaccineRecord).filter_by(id=vid, user_id=current_user.id).first()
    if record:
        db.delete(record)
        db.commit()


# ── Reminders ─────────────────────────────────────────────────────────────────

@router.post("/reminder", response_model=schemas.VaccinationReminderResponse)
def upsert_reminder(
    body: schemas.VaccinationReminderCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upsert a vaccination reminder by UUID."""
    rid = uuid.UUID(body.id) if body.id else uuid.uuid4()
    existing = db.query(models.VaccinationReminderRecord).filter_by(id=rid, user_id=current_user.id).first()
    if existing:
        existing.day_timestamp      = body.day_timestamp
        existing.hour               = body.hour
        existing.minute             = body.minute
        existing.note               = body.note or ""
        existing.is_enabled         = body.is_enabled if body.is_enabled is not None else True
        existing.notify_days_before = body.notify_days_before or ""
        db.commit()
        return _reminder_response(existing)
    record = models.VaccinationReminderRecord(
        id=rid, user_id=current_user.id,
        day_timestamp=body.day_timestamp,
        hour=body.hour, minute=body.minute,
        note=body.note or "",
        is_enabled=body.is_enabled if body.is_enabled is not None else True,
        notify_days_before=body.notify_days_before or ""
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return _reminder_response(record)


@router.get("/reminders", response_model=list[schemas.VaccinationReminderResponse])
def get_reminders(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all vaccination reminders for the logged-in user."""
    records = db.query(models.VaccinationReminderRecord).filter_by(user_id=current_user.id).all()
    return [_reminder_response(r) for r in records]


@router.delete("/reminder/{reminder_id}", status_code=204)
def delete_reminder(
    reminder_id: str,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a vaccination reminder by UUID."""
    rid = uuid.UUID(reminder_id)
    record = db.query(models.VaccinationReminderRecord).filter_by(id=rid, user_id=current_user.id).first()
    if record:
        db.delete(record)
        db.commit()
