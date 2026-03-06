from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy.orm import Session
from app.config import settings
from app.crud.refresh_token import delete_refresh_token_by_hash, get_refresh_token_by_hash
from app.crud.user import get_user_by_email, get_user_by_email_or_username, get_user_by_username
from app.database import get_db
from app.models.refresh_token import RefreshToken
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin
from app.core.security import hash_password, hash_token, verify_password
from app.core.jwt import create_access_token, create_refresh_token
from jose import jwt, JWTError

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    existing = get_user_by_email(db, user.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    existing = get_user_by_username(db, user.username)
    if existing:
        raise HTTPException(status_code=400, detail="Username already registered")

    new_user = User(
        email=user.email,
        hashed_password=hash_password(user.password),
        username=user.username,
        full_name=user.full_name
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "User created"}

@router.post("/login")
def login(user: UserLogin, response: Response, db: Session = Depends(get_db)):
    db_user = get_user_by_email_or_username(db, user.email_or_username)

    if not db_user or not verify_password(user.password, str(db_user.hashed_password)):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token(db_user.id)
    refresh_token = create_refresh_token(db_user.id)

    db_refresh = RefreshToken(
        user_id=db_user.id,
        token_hash=hash_token(refresh_token),
        expires_at=datetime.now(timezone.utc) + timedelta(days=7),
    )
    db.add(db_refresh)
    db.commit()

    response.set_cookie(
        "access_token",
        access_token,
        httponly=True,
        secure=True,
        samesite="lax",
    )

    response.set_cookie(
        "refresh_token",
        refresh_token,
        httponly=True,
        secure=True,
        samesite="lax",
    )

    return {"message": "Logged in"}

@router.post("/refresh")
def refresh(response: Response, request: Request, db: Session = Depends(get_db)):
    token = request.cookies.get("refresh_token")

    if not token:
        raise HTTPException(status_code=401)

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=settings.ALGORITHM)
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401)

        user_id = int(payload["sub"])
    except JWTError:
        raise HTTPException(status_code=401)

    db_token = get_refresh_token_by_hash(db, hash_token(token))

    if not db_token:
        raise HTTPException(status_code=401)

    db.delete(db_token)
    db.commit()

    new_access = create_access_token(user_id)
    new_refresh = create_refresh_token(user_id)

    db.add(RefreshToken(
        user_id=user_id,
        token_hash=hash_token(new_refresh),
        expires_at=datetime.now(timezone.utc) + timedelta(days=30), #change this with const or env var
    ))
    db.commit()

    response.set_cookie("access_token", new_access, httponly=True, secure=True, samesite="lax")
    response.set_cookie("refresh_token", new_refresh, httponly=True, secure=True, samesite="lax")

    return {"message": "refreshed"}

@router.post("/logout")
def logout(request: Request, response: Response, db: Session = Depends(get_db)):
    token = request.cookies.get("refresh_token")

    if token:
        delete_refresh_token_by_hash(db, hash_token(token))

    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")

    return {"message": "Logged out"}