from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.crud.activity import (
    get_activities,
    create_activity,
    get_user_activities,
    get_feed_activities,
)
from app.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.activity import ActivityResponse, ActivityFeedResponse, ActivityCreate

router = APIRouter(prefix="/activities", tags=["activities"])


@router.get("", response_model=List[ActivityResponse])
def read_activities(db: Session = Depends(get_db)):
    return get_activities(db)


@router.get("/feed", response_model=List[ActivityFeedResponse])
def read_feed(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    limit: int = 50,
    offset: int = 0,
):
    return get_feed_activities(db, current_user.id, limit=limit, offset=offset)


@router.get("/{username}", response_model=List[ActivityResponse])
def read_user_activities(username: str, db: Session = Depends(get_db)):
    return get_user_activities(db, username)

@router.post("", response_model=ActivityResponse)
def add_activity(activity: ActivityCreate, db: Session = Depends(get_db)):
    print(activity)
    return create_activity(db, activity)