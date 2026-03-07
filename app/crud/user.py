from sqlalchemy.orm import Session
from sqlalchemy import select, or_
from app.models.user import User


def get_users(db: Session, skip: int = 0, limit: int = 100):
    stmt = select(User).offset(skip).limit(limit).order_by(User.created_at.desc())
    return list(db.scalars(stmt).all())


def search_users(db: Session, q: str, skip: int = 0, limit: int = 50):
    pattern = f"%{q}%"
    stmt = (
        select(User)
        .where(
            or_(
                User.username.ilike(pattern),
                User.full_name.ilike(pattern),
            )
        )
        .offset(skip)
        .limit(limit)
        .order_by(User.created_at.desc())
    )
    return list(db.scalars(stmt).all())


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