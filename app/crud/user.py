from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.user import User

def get_user(db: Session, username: str):
    stmt = select(User).where(
        (User.username == username)
    )

    db_user = db.scalars(stmt).one_or_none()

    return db_user