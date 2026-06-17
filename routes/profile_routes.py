from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from auth import get_current_user
import models
import schemas

router = APIRouter(prefix="/profile", tags=["Profile"])


@router.get("", response_model=list[schemas.BabyProfileResponse])
def get_profiles(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all baby profiles for the logged-in user."""
    profiles = db.query(models.BabyProfile).filter_by(user_id=current_user.id).all()
    return [schemas.BabyProfileResponse(
        id=str(p.id),
        name=p.name,
        birthday_timestamp=p.birthday_timestamp,
        gender=p.gender,
        photo_base64=p.photo_base64
    ) for p in profiles]


@router.post("", response_model=schemas.BabyProfileResponse)
def create_profile(
    body: schemas.BabyProfileCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new baby profile."""
    profile = models.BabyProfile(
        user_id=current_user.id,
        name=body.name,
        birthday_timestamp=body.birthday_timestamp,
        gender=body.gender or "Other",
        photo_base64=body.photo_base64
    )
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return schemas.BabyProfileResponse(
        id=str(profile.id),
        name=profile.name,
        birthday_timestamp=profile.birthday_timestamp,
        gender=profile.gender,
        photo_base64=profile.photo_base64
    )


@router.put("/{profile_id}", response_model=schemas.BabyProfileResponse)
def update_profile(
    profile_id: str,
    body: schemas.BabyProfileUpdate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update name, birthday, gender, or photo of a baby profile."""
    profile = db.query(models.BabyProfile).filter_by(
        id=profile_id, user_id=current_user.id
    ).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    if body.name is not None:
        profile.name = body.name
    if body.birthday_timestamp is not None:
        profile.birthday_timestamp = body.birthday_timestamp
    if body.gender is not None:
        profile.gender = body.gender
    if body.photo_base64 is not None:
        profile.photo_base64 = body.photo_base64

    db.commit()
    db.refresh(profile)
    return schemas.BabyProfileResponse(
        id=str(profile.id),
        name=profile.name,
        birthday_timestamp=profile.birthday_timestamp,
        gender=profile.gender,
        photo_base64=profile.photo_base64
    )


@router.delete("/{profile_id}")
def delete_profile(
    profile_id: str,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a baby profile."""
    profile = db.query(models.BabyProfile).filter_by(
        id=profile_id, user_id=current_user.id
    ).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    db.delete(profile)
    db.commit()
    return {"ok": True}
