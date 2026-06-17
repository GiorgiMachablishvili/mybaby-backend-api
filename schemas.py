from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


# ── Auth ──────────────────────────────────────────────────────────────────────

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    name: Optional[str] = None

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    email: str
    name: Optional[str] = None


# ── Baby Profile ──────────────────────────────────────────────────────────────

class BabyProfileCreate(BaseModel):
    name: str
    birthday_timestamp: Optional[float] = None
    gender: Optional[str] = "Other"
    photo_base64: Optional[str] = None

class BabyProfileUpdate(BaseModel):
    name: Optional[str] = None
    birthday_timestamp: Optional[float] = None
    gender: Optional[str] = None
    photo_base64: Optional[str] = None

class BabyProfileResponse(BaseModel):
    id: str
    name: str
    birthday_timestamp: Optional[float] = None
    gender: str
    photo_base64: Optional[str] = None

    class Config:
        from_attributes = True


# ── Sleep ─────────────────────────────────────────────────────────────────────

class SleepSessionCreate(BaseModel):
    id: Optional[str] = None
    start: datetime
    end: datetime

class SleepSessionResponse(BaseModel):
    id: str
    start: datetime
    end: datetime

    class Config:
        from_attributes = True


# ── Feeding ───────────────────────────────────────────────────────────────────

class FeedingLogCreate(BaseModel):
    id: Optional[str] = None
    type_raw: str
    volume_text: Optional[str] = None
    notes_text: Optional[str] = None
    time_text: str
    date_text: str
    saved_at_epoch: Optional[float] = None

class FeedingLogResponse(BaseModel):
    id: str
    type_raw: str
    volume_text: Optional[str] = None
    notes_text: Optional[str] = None
    time_text: str
    date_text: str
    saved_at_epoch: Optional[float] = None

    class Config:
        from_attributes = True


# ── Diaper ────────────────────────────────────────────────────────────────────

class DiaperLogCreate(BaseModel):
    id: Optional[str] = None
    type_raw: str
    note: Optional[str] = None
    date: datetime

class DiaperLogResponse(BaseModel):
    id: str
    type_raw: str
    note: Optional[str] = None
    date: datetime

    class Config:
        from_attributes = True


# ── Sync (one call syncs everything) ─────────────────────────────────────────

class SyncRequest(BaseModel):
    sleep_sessions: list[SleepSessionCreate] = []
    feeding_logs:   list[FeedingLogCreate]   = []
    diaper_logs:    list[DiaperLogCreate]    = []

class SyncResponse(BaseModel):
    sleep_sessions: list[SleepSessionResponse] = []
    feeding_logs:   list[FeedingLogResponse]   = []
    diaper_logs:    list[DiaperLogResponse]    = []
