import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from auth import get_current_user
import models
import schemas

router = APIRouter(prefix="/growth", tags=["Growth"])


@router.post("/measurement", response_model=schemas.GrowthMeasurementResponse)
def add_measurement(
    body: schemas.GrowthMeasurementCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Save a single growth measurement (idempotent by UUID)."""
    mid = uuid.UUID(body.id) if body.id else uuid.uuid4()
    existing = db.query(models.GrowthMeasurement).filter_by(id=mid, user_id=current_user.id).first()
    if existing:
        return schemas.GrowthMeasurementResponse(
            id=str(existing.id), type_raw=existing.type_raw,
            value=existing.value, date=existing.date, percentile=existing.percentile
        )
    entry = models.GrowthMeasurement(
        id=mid, user_id=current_user.id,
        type_raw=body.type_raw, value=body.value,
        date=body.date, percentile=body.percentile
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return schemas.GrowthMeasurementResponse(
        id=str(entry.id), type_raw=entry.type_raw,
        value=entry.value, date=entry.date, percentile=entry.percentile
    )


@router.get("/measurements", response_model=list[schemas.GrowthMeasurementResponse])
def get_measurements(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all growth measurements for the logged-in user, newest first."""
    entries = (
        db.query(models.GrowthMeasurement)
        .filter_by(user_id=current_user.id)
        .order_by(models.GrowthMeasurement.date.desc())
        .all()
    )
    return [
        schemas.GrowthMeasurementResponse(
            id=str(e.id), type_raw=e.type_raw,
            value=e.value, date=e.date, percentile=e.percentile
        )
        for e in entries
    ]


@router.post("/comparison", response_model=schemas.GrowthComparisonResponse)
def set_comparison(
    body: schemas.GrowthComparisonRequest,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upsert the family height comparison data."""
    comp = db.query(models.GrowthComparison).filter_by(user_id=current_user.id).first()
    if comp:
        comp.parent1_type            = body.parent1_type
        comp.parent2_type            = body.parent2_type
        comp.parent1_height_cm       = body.parent1_height_cm
        comp.parent2_height_cm       = body.parent2_height_cm
        comp.baby_height_cm          = body.baby_height_cm
        comp.parent1_skin_tone_index = body.parent1_skin_tone_index
        comp.parent2_skin_tone_index = body.parent2_skin_tone_index
        comp.baby_skin_tone_index    = body.baby_skin_tone_index
    else:
        comp = models.GrowthComparison(
            user_id=current_user.id,
            parent1_type=body.parent1_type,
            parent2_type=body.parent2_type,
            parent1_height_cm=body.parent1_height_cm,
            parent2_height_cm=body.parent2_height_cm,
            baby_height_cm=body.baby_height_cm,
            parent1_skin_tone_index=body.parent1_skin_tone_index,
            parent2_skin_tone_index=body.parent2_skin_tone_index,
            baby_skin_tone_index=body.baby_skin_tone_index
        )
        db.add(comp)
    db.commit()
    return schemas.GrowthComparisonResponse(
        parent1_type=comp.parent1_type,
        parent2_type=comp.parent2_type,
        parent1_height_cm=comp.parent1_height_cm,
        parent2_height_cm=comp.parent2_height_cm,
        baby_height_cm=comp.baby_height_cm,
        parent1_skin_tone_index=int(comp.parent1_skin_tone_index),
        parent2_skin_tone_index=int(comp.parent2_skin_tone_index),
        baby_skin_tone_index=int(comp.baby_skin_tone_index)
    )


@router.get("/comparison", response_model=schemas.GrowthComparisonResponse)
def get_comparison(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get the family height comparison data."""
    comp = db.query(models.GrowthComparison).filter_by(user_id=current_user.id).first()
    if not comp:
        return schemas.GrowthComparisonResponse(
            parent1_type="mother", parent2_type="father",
            parent1_height_cm=None, parent2_height_cm=None, baby_height_cm=None,
            parent1_skin_tone_index=0, parent2_skin_tone_index=0, baby_skin_tone_index=0
        )
    return schemas.GrowthComparisonResponse(
        parent1_type=comp.parent1_type,
        parent2_type=comp.parent2_type,
        parent1_height_cm=comp.parent1_height_cm,
        parent2_height_cm=comp.parent2_height_cm,
        baby_height_cm=comp.baby_height_cm,
        parent1_skin_tone_index=int(comp.parent1_skin_tone_index),
        parent2_skin_tone_index=int(comp.parent2_skin_tone_index),
        baby_skin_tone_index=int(comp.baby_skin_tone_index)
    )
