from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.user import User

def get_user_by_username(db: Session, username: str):
    stmt = select(User).where(
        (User.username == username)
    )

    db_user = db.scalars(stmt).one_or_none()

    return db_user

def get_user_by_email(db: Session, email: str):
    stmt = select(User).where(
        (User.email == email)
    )

    db_user = db.scalars(stmt).one_or_none()

    return db_user

def get_user_by_email_or_username(db: Session, email_or_username: str):
    stmt = select(User).where(
        (User.email == email_or_username) |
        (User.username == email_or_username)
    )

    db_user = db.scalars(stmt).one_or_none()

    return db_user