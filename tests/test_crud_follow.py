"""Tests for follow CRUD operations."""

import pytest
from sqlalchemy.orm import Session

from app.crud.follow import follow_user, unfollow_user, get_following_ids
from app.models.user import User
from app.core.security import hash_password


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


def test_follow_user_success(db: Session):
    u1 = _create_user(db, "a@x.com", "alice")
    u2 = _create_user(db, "b@x.com", "bob")
    follow = follow_user(db, u1.id, u2.id)
    assert follow is not None
    assert follow.follower_id == u1.id
    assert follow.following_id == u2.id


def test_follow_user_self_returns_none(db: Session):
    u = _create_user(db, "c@x.com", "charlie")
    result = follow_user(db, u.id, u.id)
    assert result is None


def test_follow_user_duplicate_returns_none(db: Session):
    u1 = _create_user(db, "d@x.com", "dave")
    u2 = _create_user(db, "e@x.com", "eve")
    follow_user(db, u1.id, u2.id)
    result = follow_user(db, u1.id, u2.id)
    assert result is None


def test_unfollow_user_success(db: Session):
    u1 = _create_user(db, "f@x.com", "frank")
    u2 = _create_user(db, "g@x.com", "grace")
    follow_user(db, u1.id, u2.id)
    ok = unfollow_user(db, u1.id, u2.id)
    assert ok is True
    assert get_following_ids(db, u1.id) == []


def test_unfollow_user_not_following(db: Session):
    u1 = _create_user(db, "h@x.com", "henry")
    u2 = _create_user(db, "i@x.com", "iris")
    ok = unfollow_user(db, u1.id, u2.id)
    assert ok is False


def test_get_following_ids_empty(db: Session):
    u = _create_user(db, "j@x.com", "joe")
    assert get_following_ids(db, u.id) == []


def test_get_following_ids(db: Session):
    u1 = _create_user(db, "k@x.com", "kate")
    u2 = _create_user(db, "l@x.com", "leo")
    u3 = _create_user(db, "m@x.com", "mia")
    follow_user(db, u1.id, u2.id)
    follow_user(db, u1.id, u3.id)
    ids = get_following_ids(db, u1.id)
    assert set(ids) == {u2.id, u3.id}
