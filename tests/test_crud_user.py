"""Tests for user CRUD operations."""

import pytest
from sqlalchemy.orm import Session

from app.crud.user import (
    get_users,
    get_user_by_username,
    get_user_by_email,
    get_user_by_email_or_username,
    search_users,
)
from app.models.user import User
from app.core.security import hash_password


def _create_user(db: Session, email: str, username: str, password: str = "pass"):
    u = User(
        email=email,
        username=username,
        full_name="Full Name",
        hashed_password=hash_password(password),
    )
    db.add(u)
    db.commit()
    db.refresh(u)
    return u


def test_get_users_empty(db: Session):
    assert get_users(db) == []


def test_get_users(db: Session):
    _create_user(db, "a@x.com", "user1")
    _create_user(db, "b@x.com", "user2")
    users = get_users(db, skip=0, limit=10)
    assert len(users) == 2


def test_get_users_pagination(db: Session):
    _create_user(db, "a@x.com", "user1")
    _create_user(db, "b@x.com", "user2")
    one = get_users(db, skip=0, limit=1)
    assert len(one) == 1
    two = get_users(db, skip=0, limit=10)
    assert len(two) == 2


def test_get_user_by_username(db: Session):
    _create_user(db, "u@x.com", "alice")
    user = get_user_by_username(db, "alice")
    assert user is not None
    assert user.username == "alice"
    assert user.email == "u@x.com"


def test_get_user_by_username_not_found(db: Session):
    assert get_user_by_username(db, "nobody") is None


def test_get_user_by_email(db: Session):
    _create_user(db, "unique@x.com", "bob")
    user = get_user_by_email(db, "unique@x.com")
    assert user is not None
    assert user.email == "unique@x.com"


def test_get_user_by_email_or_username_by_email(db: Session):
    _create_user(db, "em@x.com", "charlie")
    user = get_user_by_email_or_username(db, "em@x.com")
    assert user is not None
    assert user.username == "charlie"


def test_get_user_by_email_or_username_by_username(db: Session):
    _create_user(db, "d@x.com", "dave")
    user = get_user_by_email_or_username(db, "dave")
    assert user is not None
    assert user.email == "d@x.com"


def test_search_users(db: Session):
    _create_user(db, "a@x.com", "alice")
    _create_user(db, "b@x.com", "bob")
    results = search_users(db, "ali", skip=0, limit=10)
    assert len(results) == 1
    assert results[0].username == "alice"


def test_search_users_by_full_name(db: Session):
    u = User(
        email="e@x.com",
        username="eve",
        full_name="Eve Smith",
        hashed_password=hash_password("x"),
    )
    db.add(u)
    db.commit()
    db.refresh(u)
    results = search_users(db, "Smith", skip=0, limit=10)
    assert len(results) == 1
    assert results[0].username == "eve"
