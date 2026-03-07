"""
Pytest configuration and shared fixtures for cafeina-api.
Uses an in-memory SQLite database. StaticPool ensures a single connection
so all sessions see the same DB (SQLite :memory: is per-connection otherwise).
"""
import os

# Set test env before any app imports that read config
os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")
os.environ.setdefault("SECRET_KEY", "test-secret-key-for-pytest")
os.environ.setdefault("ALGORITHM", "HS256")
os.environ.setdefault("ACCESS_TOKEN_EXPIRE_MINUTES", "30")
os.environ.setdefault("REFRESH_TOKEN_EXPIRE_DAYS", "7")
os.environ.setdefault("CORS_ORIGINS", '["http://localhost"]')
os.environ.setdefault("GOOGLE_MAPS_API_KEY", "test-google-maps-key")

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from app.database import Base, get_db
from app.main import app

# Import all models so they are registered with Base.metadata
from app.models import user as _user  # noqa: F401
from app.models import cafe as _cafe  # noqa: F401
from app.models import activity as _activity  # noqa: F401
from app.models import follow as _follow  # noqa: F401
from app.models import refresh_token as _refresh_token  # noqa: F401

TEST_DATABASE_URL = os.environ["DATABASE_URL"]
if TEST_DATABASE_URL.startswith("sqlite"):
    # Single connection so :memory: is shared by all sessions
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
else:
    engine = create_engine(TEST_DATABASE_URL)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="function")
def db() -> Session:
    """Create a fresh DB session and tables for each test."""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(db: Session):
    """TestClient that uses the overridden get_db. HTTPS base_url so secure cookies are sent."""
    yield TestClient(app, base_url="https://testserver")


@pytest.fixture
def test_user(client: TestClient):
    """Create a test user via API and return (email, username, password)."""
    data = {
        "email": "test@example.com",
        "username": "testuser",
        "password": "testpass123",
        "fullName": "Test User",
    }
    resp = client.post("/auth/register", json=data)
    assert resp.status_code == 200
    return {
        "email": data["email"],
        "username": data["username"],
        "password": data["password"],
        "full_name": data["fullName"],
    }


@pytest.fixture
def auth_headers(client: TestClient, test_user: dict):
    """Log in and return headers with cookies (client keeps cookies by default)."""
    client.post(
        "/auth/login",
        json={
            "emailOrUsername": test_user["email"],
            "password": test_user["password"],
        },
    )
    return {}
