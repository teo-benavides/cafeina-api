from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.models.follow import Follow


def follow_user(db: Session, follower_id: int, following_id: int) -> Follow | None:
    if follower_id == following_id:
        return None
    follow = Follow(follower_id=follower_id, following_id=following_id)
    db.add(follow)
    try:
        db.commit()
        db.refresh(follow)
        return follow
    except IntegrityError:
        db.rollback()
        return None


def unfollow_user(db: Session, follower_id: int, following_id: int) -> bool:
    stmt = select(Follow).where(
        Follow.follower_id == follower_id,
        Follow.following_id == following_id,
    )
    follow = db.scalars(stmt).one_or_none()
    if follow:
        db.delete(follow)
        db.commit()
        return True
    return False


def get_following_ids(db: Session, user_id: int) -> list[int]:
    result = db.execute(select(Follow.following_id).where(Follow.follower_id == user_id))
    return list(result.scalars().all())
