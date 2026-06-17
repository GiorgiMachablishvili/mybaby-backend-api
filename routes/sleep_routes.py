import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from auth import get_current_user
import models
import schemas

router = APIRouter(prefix="/sleep", tags=["Sleep"])


@router.post("", response_model=schemas.SleepSessionResponse)
def add_sleep(
    body: schemas.SleepSessionCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Save a single sleep session (timer stop or log past sleep)."""
    sid = uuid.UUID(body.id) if body.id else uuid.uuid4()
    existing = db.query(models.SleepSession).filter_by(id=sid, user_id=current_user.id).first()
    if existing:
        return schemas.SleepSessionResponse(
            id=str(existing.id), start=existing.start, end=existing.end
        )
    session = models.SleepSession(
        id=sid, user_id=current_user.id, start=body.start, end=body.end
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return schemas.SleepSessionResponse(id=str(session.id), start=session.start, end=session.end)


@router.get("", response_model=list[schemas.SleepSessionResponse])
def get_sleep(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all sleep sessions for the logged-in user, newest first."""
    sessions = (
        db.query(models.SleepSession)
        .filter_by(user_id=current_user.id)
        .order_by(models.SleepSession.start.desc())
        .all()
    )
    return [
        schemas.SleepSessionResponse(id=str(s.id), start=s.start, end=s.end)
        for s in sessions
    ]


@router.post("/goal", response_model=schemas.SleepGoalResponse)
def set_goal(
    body: schemas.SleepGoalRequest,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Set or update the daily sleep goal."""
    goal = db.query(models.SleepGoal).filter_by(user_id=current_user.id).first()
    if goal:
        goal.goal_hours = body.goal_hours
    else:
        goal = models.SleepGoal(user_id=current_user.id, goal_hours=body.goal_hours)
        db.add(goal)
    db.commit()
    return schemas.SleepGoalResponse(goal_hours=goal.goal_hours)


@router.get("/goal", response_model=schemas.SleepGoalResponse)
def get_goal(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get the daily sleep goal. Returns 14h default if not set."""
    goal = db.query(models.SleepGoal).filter_by(user_id=current_user.id).first()
    return schemas.SleepGoalResponse(goal_hours=goal.goal_hours if goal else 14.0)
