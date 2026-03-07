"""Tests for /follows endpoints."""

import pytest
from fastapi.testclient import TestClient


def test_follow_requires_auth(client: TestClient, test_user: dict):
    resp = client.post(f"/follows/{test_user['username']}")
    assert resp.status_code == 401


def test_follow_success(client: TestClient, test_user: dict, auth_headers: dict):
    # Create another user to follow
    client.post(
        "/auth/register",
        json={
            "email": "other@example.com",
            "username": "otheruser",
            "password": "pass123",
            "fullName": "Other User",
        },
    )
    resp = client.post("/follows/otheruser")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_follow_already_following(client: TestClient, test_user: dict, auth_headers: dict):
    client.post(
        "/auth/register",
        json={
            "email": "dup@example.com",
            "username": "dupuser",
            "password": "pass123",
            "fullName": "Dup",
        },
    )
    client.post("/follows/dupuser")
    resp = client.post("/follows/dupuser")
    assert resp.status_code == 400
    assert "already following" in resp.json()["detail"].lower() or "cannot follow" in resp.json()["detail"].lower()


def test_follow_self_fails(client: TestClient, test_user: dict, auth_headers: dict):
    resp = client.post(f"/follows/{test_user['username']}")
    assert resp.status_code == 400


def test_follow_user_not_found(client: TestClient, auth_headers: dict):
    resp = client.post("/follows/nonexistentuser999")
    assert resp.status_code == 404
    assert "not found" in resp.json()["detail"].lower()


def test_unfollow_requires_auth(client: TestClient, test_user: dict):
    resp = client.delete(f"/follows/{test_user['username']}")
    assert resp.status_code == 401


def test_unfollow_success(client: TestClient, test_user: dict, auth_headers: dict):
    client.post(
        "/auth/register",
        json={
            "email": "unfollow@example.com",
            "username": "unfollowuser",
            "password": "pass123",
            "fullName": "Unfollow",
        },
    )
    client.post("/follows/unfollowuser")
    resp = client.delete("/follows/unfollowuser")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_unfollow_not_following(client: TestClient, test_user: dict, auth_headers: dict):
    client.post(
        "/auth/register",
        json={
            "email": "never@example.com",
            "username": "neverfollowed",
            "password": "pass123",
            "fullName": "Never",
        },
    )
    resp = client.delete("/follows/neverfollowed")
    assert resp.status_code == 404
    assert "not following" in resp.json()["detail"].lower()


def test_unfollow_user_not_found(client: TestClient, auth_headers: dict):
    resp = client.delete("/follows/nonexistentuser999")
    assert resp.status_code == 404
