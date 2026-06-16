from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from auth import hash_password, verify_password, create_access_token, get_current_user
import models
import schemas

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=schemas.TokenResponse)
def register(body: schemas.RegisterRequest, db: Session = Depends(get_db)):
    """Create a new account with email + password."""
    if db.query(models.User).filter(models.User.email == body.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    user = models.User(
        email=body.email,
        password_hash=hash_password(body.password),
        name=body.name
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    return schemas.TokenResponse(
        access_token=create_access_token(str(user.id)),
        user_id=str(user.id),
        email=user.email,
        name=user.name
    )


@router.post("/login", response_model=schemas.TokenResponse)
def login(body: schemas.LoginRequest, db: Session = Depends(get_db)):
    """Login with email + password. Returns a JWT token."""
    user = db.query(models.User).filter(models.User.email == body.email).first()
    if not user or not user.password_hash or not verify_password(body.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    return schemas.TokenResponse(
        access_token=create_access_token(str(user.id)),
        user_id=str(user.id),
        email=user.email,
        name=user.name
    )


@router.get("/me")
def me(current_user: models.User = Depends(get_current_user)):
    """Return the logged-in user's info."""
    return {
        "user_id": str(current_user.id),
        "email":   current_user.email,
        "name":    current_user.name
    }
