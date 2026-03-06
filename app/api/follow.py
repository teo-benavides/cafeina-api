from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.crud.follow import follow_user, unfollow_user
from app.crud.user import get_user_by_username
from app.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User

router = APIRouter(prefix="/follows", tags=["follows"])


@router.post("/{username}")
def follow(
    username: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    target = get_user_by_username(db, username)
    if not target:
        raise HTTPException(status_code=404, detail="User not found")
    if not follow_user(db, current_user.id, target.id):
        raise HTTPException(
            status_code=400,
            detail="Already following or cannot follow yourself",
        )
    return {"status": "ok"}


@router.delete("/{username}")
def unfollow(
    username: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    target = get_user_by_username(db, username)
    if not target:
        raise HTTPException(status_code=404, detail="User not found")
    if not unfollow_user(db, current_user.id, target.id):
        raise HTTPException(status_code=404, detail="Not following")
    return {"status": "ok"}
