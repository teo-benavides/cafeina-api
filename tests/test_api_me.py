"""Tests for /me endpoint (authenticated current user)."""

import pytest
from fastapi.testclient import TestClient


def test_me_returns_current_user(client: TestClient, test_user: dict, auth_headers: dict):
    resp = client.get("/me")
    assert resp.status_code == 200
    data = resp.json()
    assert data["username"] == test_user["username"]
    assert data["fullName"] == test_user["full_name"]
    assert isinstance(data["id"], int)


def test_me_requires_auth(client: TestClient):
    resp = client.get("/me")
    assert resp.status_code == 401


def test_me_invalid_token(client: TestClient):
    client.cookies.set("access_token", "invalid.jwt.here")
    resp = client.get("/me")
    assert resp.status_code == 401


def test_me_refresh_token_rejected(client: TestClient, test_user: dict):
    """Using a refresh token as access_token yields 401 (wrong token_type)."""
    client.post(
        "/auth/login",
        json={"emailOrUsername": test_user["email"], "password": test_user["password"]},
    )
    refresh_val = client.cookies.get("refresh_token")
    client.cookies.delete("access_token")
    client.cookies.set("access_token", refresh_val)
    resp = client.get("/me")
    assert resp.status_code == 401


def test_me_user_not_found(client: TestClient, test_user: dict, db):
    """If user was deleted after login, /me returns 401."""
    from app.models.user import User
    client.post(
        "/auth/login",
        json={"emailOrUsername": test_user["email"], "password": test_user["password"]},
    )
    me_resp = client.get("/me")
    assert me_resp.status_code == 200
    user_id = me_resp.json()["id"]
    user = db.get(User, user_id)
    assert user is not None
    db.delete(user)
    db.commit()
    resp = client.get("/me")
    assert resp.status_code == 401
