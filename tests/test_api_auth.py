"""Tests for /auth endpoints: register, login, refresh, logout."""

import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient


def test_register_ok(client: TestClient):
    resp = client.post(
        "/auth/register",
        json={
            "email": "new@example.com",
            "username": "newuser",
            "password": "secret123",
            "fullName": "New User",
        },
    )
    assert resp.status_code == 200
    assert resp.json() == {"message": "User created"}


def test_register_full_name_empty_becomes_none(client: TestClient):
    """UserCreate validator converts fullName '' to None."""
    client.post(
        "/auth/register",
        json={
            "email": "noname@example.com",
            "username": "nonameuser",
            "password": "secret123",
            "fullName": "",
        },
    )
    client.post(
        "/auth/login",
        json={"emailOrUsername": "nonameuser", "password": "secret123"},
    )
    resp = client.get("/me")
    assert resp.status_code == 200
    assert resp.json()["fullName"] is None


def test_register_duplicate_email(client: TestClient, test_user: dict):
    resp = client.post(
        "/auth/register",
        json={
            "email": test_user["email"],
            "username": "otheruser",
            "password": "secret123",
            "fullName": "Other",
        },
    )
    assert resp.status_code == 400
    assert "already registered" in resp.json()["detail"].lower()


def test_register_duplicate_username(client: TestClient, test_user: dict):
    resp = client.post(
        "/auth/register",
        json={
            "email": "other@example.com",
            "username": test_user["username"],
            "password": "secret123",
            "fullName": "Other",
        },
    )
    assert resp.status_code == 400
    assert "username" in resp.json()["detail"].lower()


def test_login_ok(client: TestClient, test_user: dict):
    resp = client.post(
        "/auth/login",
        json={
            "emailOrUsername": test_user["email"],
            "password": test_user["password"],
        },
    )
    assert resp.status_code == 200
    assert resp.json() == {"message": "Logged in"}
    assert "access_token" in resp.cookies
    assert "refresh_token" in resp.cookies


def test_login_with_username(client: TestClient, test_user: dict):
    resp = client.post(
        "/auth/login",
        json={
            "emailOrUsername": test_user["username"],
            "password": test_user["password"],
        },
    )
    assert resp.status_code == 200
    assert resp.json() == {"message": "Logged in"}


def test_login_invalid_credentials(client: TestClient, test_user: dict):
    resp = client.post(
        "/auth/login",
        json={
            "emailOrUsername": test_user["email"],
            "password": "wrongpassword",
        },
    )
    assert resp.status_code == 401


def test_logout_ok(client: TestClient, test_user: dict, auth_headers: dict):
    resp = client.post("/auth/logout")
    assert resp.status_code == 200
    assert resp.json() == {"message": "Logged out"}


def test_logout_with_refresh_cookie_deletes_token(client: TestClient, test_user: dict):
    """Logout when a refresh_token cookie is present hits delete_refresh_token_by_hash."""
    client.post(
        "/auth/login",
        json={"emailOrUsername": test_user["email"], "password": test_user["password"]},
    )
    resp = client.post("/auth/logout")
    assert resp.status_code == 200


def test_refresh_no_cookie(client: TestClient):
    resp = client.post("/auth/refresh")
    assert resp.status_code == 401


def test_refresh_success(client: TestClient, test_user: dict):
    client.post(
        "/auth/login",
        json={"emailOrUsername": test_user["email"], "password": test_user["password"]},
    )
    resp = client.post("/auth/refresh")
    assert resp.status_code == 200
    assert resp.json() == {"message": "refreshed"}
    assert "access_token" in resp.cookies
    assert "refresh_token" in resp.cookies


def test_refresh_invalid_token(client: TestClient):
    client.cookies.set("refresh_token", "invalid.jwt.token")
    resp = client.post("/auth/refresh")
    assert resp.status_code == 401


def test_refresh_access_token_rejected(client: TestClient, test_user: dict):
    """Using access_token as refresh_token yields 401 (wrong token_type)."""
    from app.core.jwt import create_access_token
    client.post(
        "/auth/login",
        json={"emailOrUsername": test_user["email"], "password": test_user["password"]},
    )
    me_resp = client.get("/me")
    user_id = me_resp.json()["id"]
    access = create_access_token(user_id)
    client.cookies.set("refresh_token", access)
    resp = client.post("/auth/refresh")
    assert resp.status_code == 401


def test_refresh_token_not_in_db(client: TestClient, test_user: dict, db):
    """Refresh with valid JWT but token already deleted from DB returns 401."""
    from app.crud.refresh_token import get_refresh_token_by_hash
    from app.core.security import hash_token
    client.post(
        "/auth/login",
        json={"emailOrUsername": test_user["email"], "password": test_user["password"]},
    )
    refresh_cookie = client.cookies.get("refresh_token")
    assert refresh_cookie
    # Delete the refresh token from DB (e.g. already used or revoked)
    token_row = get_refresh_token_by_hash(db, hash_token(refresh_cookie))
    assert token_row is not None
    db.delete(token_row)
    db.commit()
    resp = client.post("/auth/refresh")
    assert resp.status_code == 401


def test_me_after_login(client: TestClient, test_user: dict, auth_headers: dict):
    resp = client.get("/me")
    assert resp.status_code == 200
    data = resp.json()
    assert data["username"] == test_user["username"]
    assert "id" in data


def test_me_unauthorized(client: TestClient):
    resp = client.get("/me")
    assert resp.status_code == 401
