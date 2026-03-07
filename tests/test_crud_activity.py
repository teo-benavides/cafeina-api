"""Tests for activity CRUD operations."""

import pytest
from sqlalchemy.orm import Session

from app.crud.activity import (
    get_activities,
    get_user_activities,
    create_activity,
    get_feed_activities,
)
from app.crud.cafe import create_cafe as crud_create_cafe
from app.crud.follow import follow_user
from app.crud.user import get_user_by_username
from app.models.user import User
from app.schemas.activity import ActivityCreate
from app.schemas.cafe import CafeCreate
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


def test_get_activities_empty(db: Session):
    assert get_activities(db) == []


def test_create_activity(db: Session):
    u = _create_user(db, "u@x.com", "alice")
    cafe = crud_create_cafe(
        db,
        CafeCreate(
            name="Café",
            address="1 St",
            maps_id="place_1",
            maps_url="https://maps.google.com/1",
        ),
    )
    activity_in = ActivityCreate(
        user_id=u.id,
        cafe_id=cafe.id,
        rating=4,
        favorite=True,
        review="Good",
    )
    activity = create_activity(db, activity_in)
    assert activity.id is not None
    assert activity.rating == 4
    assert activity.review == "Good"
    assert activity.user_id == u.id
    assert activity.cafe_id == cafe.id


def test_get_activities(db: Session):
    u = _create_user(db, "a@x.com", "user1")
    cafe = crud_create_cafe(
        db,
        CafeCreate(name="C", address="1", maps_id="p1", maps_url="https://x.com/1"),
    )
    create_activity(
        db,
        ActivityCreate(user_id=u.id, cafe_id=cafe.id, rating=3, favorite=False, review=None),
    )
    activities = get_activities(db)
    assert len(activities) == 1
    assert activities[0].rating == 3


def test_get_user_activities(db: Session):
    u = _create_user(db, "b@x.com", "bob")
    cafe = crud_create_cafe(
        db,
        CafeCreate(name="D", address="2", maps_id="p2", maps_url="https://x.com/2"),
    )
    create_activity(
        db,
        ActivityCreate(user_id=u.id, cafe_id=cafe.id, rating=5, favorite=True, review="Great"),
    )
    result = get_user_activities(db, "bob")
    assert len(result) == 1
    assert result[0].review == "Great"


def test_get_user_activities_unknown_username(db: Session):
    assert get_user_activities(db, "nobody") == []


def test_get_feed_activities(db: Session):
    u1 = _create_user(db, "u1@x.com", "user1")
    u2 = _create_user(db, "u2@x.com", "user2")
    cafe = crud_create_cafe(
        db,
        CafeCreate(name="E", address="3", maps_id="p3", maps_url="https://x.com/3"),
    )
    create_activity(
        db,
        ActivityCreate(user_id=u1.id, cafe_id=cafe.id, rating=1, favorite=False, review="A"),
    )
    create_activity(
        db,
        ActivityCreate(user_id=u2.id, cafe_id=cafe.id, rating=2, favorite=True, review="B"),
    )
    # Feed for u1 only (no follows) = just u1's activity
    feed = get_feed_activities(db, u1.id, limit=10)
    assert len(feed) == 1
    assert feed[0].user_id == u1.id


def test_get_feed_activities_includes_following(db: Session):
    u1 = _create_user(db, "u1@x.com", "feed_user1")
    u2 = _create_user(db, "u2@x.com", "feed_user2")
    cafe = crud_create_cafe(
        db,
        CafeCreate(name="F", address="4", maps_id="p4", maps_url="https://x.com/4"),
    )
    create_activity(
        db,
        ActivityCreate(user_id=u1.id, cafe_id=cafe.id, rating=1, favorite=False, review="Own"),
    )
    create_activity(
        db,
        ActivityCreate(user_id=u2.id, cafe_id=cafe.id, rating=2, favorite=True, review="Following"),
    )
    follow_user(db, u1.id, u2.id)
    feed = get_feed_activities(db, u1.id, limit=10)
    assert len(feed) == 2
    reviews = {a.review for a in feed}
    assert reviews == {"Own", "Following"}
