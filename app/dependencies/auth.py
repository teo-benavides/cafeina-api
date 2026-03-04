from fastapi import Depends, HTTPException, Request
from jose import jwt, JWTError
from pydantic import ValidationError
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.config import settings
from app.schemas.token_payload import TokenPayload

def get_current_user(
    request: Request,
    db: Session = Depends(get_db)
):
    token = request.cookies.get("access_token")

    if not token:
        raise HTTPException(status_code=401)

    try:
        raw_payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        payload = TokenPayload.model_validate(raw_payload)
    except (JWTError, ValidationError):
        raise HTTPException(status_code=401)

    if payload.token_type != "access":
        raise HTTPException(status_code=401)

    user_id = int(payload.sub)

    user = db.get(User, user_id)

    if not user:
        raise HTTPException(status_code=401)

    return user