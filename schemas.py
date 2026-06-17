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

class SleepGoalRequest(BaseModel):
    goal_hours: float

class SleepGoalResponse(BaseModel):
    goal_hours: float

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


# ── Vaccination ───────────────────────────────────────────────────────────────

class VaccineRecordCreate(BaseModel):
    id: Optional[str] = None
    name: str
    full_name: str
    age_range: Optional[str] = ""
    due_date_timestamp: Optional[float] = None
    scheduled_timestamp: Optional[float] = None
    scheduled_hour: Optional[float] = None
    scheduled_minute: Optional[float] = None
    completed_timestamp: Optional[float] = None
    dose_number: Optional[float] = None
    total_doses: Optional[float] = None
    doctor_name: Optional[str] = None
    notes: Optional[str] = ""

class VaccineRecordResponse(BaseModel):
    id: str
    name: str
    full_name: str
    age_range: str
    due_date_timestamp: Optional[float] = None
    scheduled_timestamp: Optional[float] = None
    scheduled_hour: Optional[float] = None
    scheduled_minute: Optional[float] = None
    completed_timestamp: Optional[float] = None
    dose_number: Optional[float] = None
    total_doses: Optional[float] = None
    doctor_name: Optional[str] = None
    notes: str

    class Config:
        from_attributes = True

class VaccinationReminderCreate(BaseModel):
    id: Optional[str] = None
    day_timestamp: float
    hour: float
    minute: float
    note: Optional[str] = ""
    is_enabled: Optional[bool] = True
    notify_days_before: Optional[str] = ""   # comma-separated e.g. "1,3"

class VaccinationReminderResponse(BaseModel):
    id: str
    day_timestamp: float
    hour: float
    minute: float
    note: str
    is_enabled: bool
    notify_days_before: str

    class Config:
        from_attributes = True


# ── Growth ────────────────────────────────────────────────────────────────────

class GrowthMeasurementCreate(BaseModel):
    id: Optional[str] = None
    type_raw: str
    value: float
    date: datetime
    percentile: Optional[float] = None

class GrowthMeasurementResponse(BaseModel):
    id: str
    type_raw: str
    value: float
    date: datetime
    percentile: Optional[float] = None

    class Config:
        from_attributes = True

class GrowthComparisonRequest(BaseModel):
    parent1_type: str
    parent2_type: str
    parent1_height_cm: Optional[float] = None
    parent2_height_cm: Optional[float] = None
    baby_height_cm: Optional[float] = None
    parent1_skin_tone_index: int = 0
    parent2_skin_tone_index: int = 0
    baby_skin_tone_index: int = 0

class GrowthComparisonResponse(BaseModel):
    parent1_type: str
    parent2_type: str
    parent1_height_cm: Optional[float] = None
    parent2_height_cm: Optional[float] = None
    baby_height_cm: Optional[float] = None
    parent1_skin_tone_index: int
    parent2_skin_tone_index: int
    baby_skin_tone_index: int

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
