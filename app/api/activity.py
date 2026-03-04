from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.database import SessionLocal
from app.schemas.activity import ActivityResponse, ActivityCreate
from app.crud.activity import get_activities, create_activity

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/", response_model=List[ActivityResponse])
def read_activities(db: Session = Depends(get_db)):
    return get_activities(db)

@router.post("/", response_model=ActivityResponse)
def add_activity(activity: ActivityCreate, db: Session = Depends(get_db)):
    return create_activity(db, activity)