from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload
from app.crud.follow import get_following_ids
from app.crud.user import get_user_by_username
from app.models.activity import Activity
from app.schemas.activity import ActivityCreate

def get_activities(db: Session):
    return db.scalars(
        select(Activity).options(joinedload(Activity.cafe))
    ).all()

def get_user_activities(db: Session, username: str) -> list[Activity]:
    user = get_user_by_username(db, username)

    if not user:
        return []
    
    return list(
        db.scalars(
            select(Activity).options(joinedload(Activity.cafe)).filter(Activity.user_id == user.id)
        ).all()
    )

def create_activity(db: Session, activity: ActivityCreate):
    db_activity = Activity(**activity.model_dump())
    db.add(db_activity)
    db.commit()
    db.refresh(db_activity)
    return db_activity


def get_feed_activities(
    db: Session, user_id: int, limit: int = 50, offset: int = 0
) -> list[Activity]:
    following_ids = get_following_ids(db, user_id)
    feed_user_ids = [user_id] + following_ids
    return list(
        db.scalars(
            select(Activity)
            .options(joinedload(Activity.cafe), joinedload(Activity.user))
            .where(Activity.user_id.in_(feed_user_ids))
            .order_by(Activity.created_at.desc())
            .limit(limit)
            .offset(offset)
        ).all()
    )