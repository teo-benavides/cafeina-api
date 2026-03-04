from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.activity import Activity
from app.schemas.activity import ActivityCreate
from sqlalchemy.orm import joinedload

def get_activities(db: Session):
    return db.scalars(
        select(Activity).options(joinedload(Activity.cafe))
    ).all()

def create_activity(db: Session, activity: ActivityCreate):
    db_activity = Activity(**activity.model_dump())
    db.add(db_activity)
    db.commit()
    db.refresh(db_activity)
    return db_activity