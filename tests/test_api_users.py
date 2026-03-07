"""Tests for /users endpoints."""

import pytest
from fastapi.testclient import TestClient


def test_list_users_empty(client: TestClient):
    resp = client.get("/users")
    assert resp.status_code == 200
    assert resp.json() == []


def test_list_users(client: TestClient, test_user: dict):
    resp = client.get("/users")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["username"] == test_user["username"]
    assert "fullName" in data[0]


def test_list_users_pagination(client: TestClient, test_user: dict):
    resp = client.get("/users?skip=0&limit=10")
    assert resp.status_code == 200
    assert len(resp.json()) == 1


def test_search_users(client: TestClient, test_user: dict):
    resp = client.get("/users/search?q=test")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) >= 1
    assert any(u["username"] == test_user["username"] for u in data)


def test_search_users_empty_query_fails(client: TestClient):
    resp = client.get("/users/search?q=")
    assert resp.status_code == 422


def test_get_user_by_username(client: TestClient, test_user: dict):
    resp = client.get(f"/users/by-username/{test_user['username']}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["username"] == test_user["username"]


def test_get_user_by_username_not_found(client: TestClient):
    resp = client.get("/users/by-username/nonexistentuser123")
    assert resp.status_code == 404
    assert "not found" in resp.json()["detail"].lower()
