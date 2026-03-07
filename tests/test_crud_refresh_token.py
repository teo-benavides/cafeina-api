"""Tests for refresh_token CRUD operations."""

import pytest
from sqlalchemy.orm import Session

from app.crud.refresh_token import get_refresh_token_by_hash, delete_refresh_token_by_hash
from app.models.refresh_token import RefreshToken
from app.models.user import User
from app.core.security import hash_password
from datetime import datetime, timezone, timedelta


def _create_user(db: Session, email: str, username: str) -> User:
    u = User(
        email=email,
        username=username,
        full_name="User",
        hashed_password=hash_password("pass"),
    )
    db.add(u)
    db.commit()
    db.refresh(u)
    return u


def test_get_refresh_token_by_hash_not_found(db: Session):
    assert get_refresh_token_by_hash(db, "nonexistent_hash") is None


def test_get_refresh_token_by_hash_found(db: Session):
    u = _create_user(db, "a@x.com", "alice")
    token_hash = "abc123hash"
    rt = RefreshToken(
        user_id=u.id,
        token_hash=token_hash,
        expires_at=datetime.now(timezone.utc) + timedelta(days=7),
    )
    db.add(rt)
    db.commit()
    db.refresh(rt)
    found = get_refresh_token_by_hash(db, token_hash)
    assert found is not None
    assert found.user_id == u.id
    assert found.token_hash == token_hash


def test_delete_refresh_token_by_hash(db: Session):
    u = _create_user(db, "b@x.com", "bob")
    token_hash = "def456hash"
    rt = RefreshToken(
        user_id=u.id,
        token_hash=token_hash,
        expires_at=datetime.now(timezone.utc) + timedelta(days=7),
    )
    db.add(rt)
    db.commit()
    assert get_refresh_token_by_hash(db, token_hash) is not None
    delete_refresh_token_by_hash(db, token_hash)
    assert get_refresh_token_by_hash(db, token_hash) is None
