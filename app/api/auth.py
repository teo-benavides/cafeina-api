from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.config import settings
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
    existing = db.query(User).filter(User.email == user.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    existing = db.query(User).filter(User.username == user.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already registered")

    new_user = User(
        email=user.email,
        hashedPassword=hash_password(user.password),
        username=user.username,
        fullName=user.fullName
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "User created"}

@router.post("/login")
def login(user: UserLogin, response: Response, db: Session = Depends(get_db)):
    stmt = select(User).where(
        (User.email == user.emailOrUsername) |
        (User.username == user.emailOrUsername)
    )

    result = db.execute(stmt)
    db_user = result.scalar_one_or_none()
    
    if not db_user or not verify_password(user.password, str(db_user.hashedPassword)):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token(db_user.userId)
    refresh_token = create_refresh_token(db_user.userId)

    db_refresh = RefreshToken(
        userId=db_user.userId,
        tokenHash=hash_token(refresh_token),
        expiresAt=datetime.now(timezone.utc) + timedelta(days=7),
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

    token_hash = hash_token(token)
    db_token = db.query(RefreshToken).filter(
        RefreshToken.token_hash == token_hash
    ).first()

    if not db_token:
        raise HTTPException(status_code=401)

    db.delete(db_token)
    db.commit()

    new_access = create_access_token(user_id)
    new_refresh = create_refresh_token(user_id)

    db.add(RefreshToken(
        userId=user_id,
        tokenHash=hash_token(new_refresh),
        expiresAt=datetime.now(timezone.utc) + timedelta(days=30), #change this with const or env var
    ))
    db.commit()

    response.set_cookie("access_token", new_access, httponly=True, secure=True, samesite="lax")
    response.set_cookie("refresh_token", new_refresh, httponly=True, secure=True, samesite="lax")

    return {"message": "refreshed"}

@router.post("/logout")
def logout(request: Request, response: Response, db: Session = Depends(get_db)):
    token = request.cookies.get("refresh_token")

    if token:
        db.query(RefreshToken).filter(
            RefreshToken.token_hash == hash_token(token)
        ).delete()
        db.commit()

    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")

    return {"message": "Logged out"}