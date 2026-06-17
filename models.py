import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Float, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from database import Base


class User(Base):
    __tablename__ = "users"

    id            = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email         = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=True)   # nullable → future social login
    name          = Column(String, nullable=True)
    created_at    = Column(DateTime, default=datetime.utcnow)

    sleep_sessions       = relationship("SleepSession",      back_populates="user", cascade="all, delete")
    feeding_logs         = relationship("FeedingLog",        back_populates="user", cascade="all, delete")
    diaper_logs          = relationship("DiaperLog",         back_populates="user", cascade="all, delete")
    baby_profiles        = relationship("BabyProfile",       back_populates="user", cascade="all, delete")
    sleep_goal           = relationship("SleepGoal",         back_populates="user", cascade="all, delete", uselist=False)
    growth_measurements  = relationship("GrowthMeasurement", back_populates="user", cascade="all, delete")
    growth_comparison    = relationship("GrowthComparison",  back_populates="user", cascade="all, delete", uselist=False)


class BabyProfile(Base):
    __tablename__ = "baby_profiles"

    id                  = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id             = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    name                = Column(String, nullable=False)
    birthday_timestamp  = Column(Float, nullable=True)
    gender              = Column(String, default="Other")
    photo_base64        = Column(String, nullable=True)
    created_at          = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="baby_profiles")


class SleepSession(Base):
    __tablename__ = "sleep_sessions"

    id         = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id    = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    start      = Column(DateTime, nullable=False)
    end        = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="sleep_sessions")


class FeedingLog(Base):
    __tablename__ = "feeding_logs"

    id              = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id         = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    type_raw        = Column(String, nullable=False)   # breast / bottle / formula / solid
    volume_text     = Column(String, nullable=True)
    notes_text      = Column(String, nullable=True)
    time_text       = Column(String, nullable=False)
    date_text       = Column(String, nullable=False)
    saved_at_epoch  = Column(Float,  nullable=True)
    created_at      = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="feeding_logs")


class SleepGoal(Base):
    __tablename__ = "sleep_goals"

    id         = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id    = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, unique=True)
    goal_hours = Column(Float, nullable=False, default=14.0)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="sleep_goal")


class GrowthMeasurement(Base):
    __tablename__ = "growth_measurements"

    id          = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id     = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    type_raw    = Column(String, nullable=False)   # weight / height / head
    value       = Column(Float, nullable=False)
    date        = Column(DateTime, nullable=False)
    percentile  = Column(Float, nullable=True)
    created_at  = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="growth_measurements")


class GrowthComparison(Base):
    __tablename__ = "growth_comparisons"

    id                     = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id                = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, unique=True)
    parent1_type           = Column(String, default="mother")
    parent2_type           = Column(String, default="father")
    parent1_height_cm      = Column(Float, nullable=True)
    parent2_height_cm      = Column(Float, nullable=True)
    baby_height_cm         = Column(Float, nullable=True)
    parent1_skin_tone_index = Column(Float, default=0)
    parent2_skin_tone_index = Column(Float, default=0)
    baby_skin_tone_index   = Column(Float, default=0)
    updated_at             = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="growth_comparison")


class DiaperLog(Base):
    __tablename__ = "diaper_logs"

    id         = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id    = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    type_raw   = Column(String, nullable=False)   # wet / dirty / mixed
    note       = Column(String, nullable=True)
    date       = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="diaper_logs")
