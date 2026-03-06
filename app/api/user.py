from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.user import UserResponse
from app.crud.user import get_user_by_username

router = APIRouter(prefix="/users", tags=["users"])

@router.get("", response_model=UserResponse)
def read_user(username: str = Query(..., description="Username"), db: Session = Depends(get_db)):
    return get_user_by_username(db, username)
