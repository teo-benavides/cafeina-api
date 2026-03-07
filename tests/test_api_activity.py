"""Tests for /activities endpoints."""

import pytest
from fastapi.testclient import TestClient


def test_list_activities_empty(client: TestClient):
    resp = client.get("/activities")
    assert resp.status_code == 200
    assert resp.json() == []


def test_add_activity(client: TestClient, test_user: dict):
    # Create a cafe first
    cafe_resp = client.post(
        "/cafes",
        json={
            "name": "Activity Test Café",
            "address": "1 Main St",
            "mapsId": "place_activity",
            "mapsUrl": "https://maps.google.com/place_activity",
        },
    )
    assert cafe_resp.status_code == 200
    cafe_id = cafe_resp.json()["id"]
    # Get current user id via /me (need to log in)
    client.post(
        "/auth/login",
        json={
            "emailOrUsername": test_user["email"],
            "password": test_user["password"],
        },
    )
    me_resp = client.get("/me")
    assert me_resp.status_code == 200
    user_id = me_resp.json()["id"]

    resp = client.post(
        "/activities",
        json={
            "userId": user_id,
            "cafeId": cafe_id,
            "rating": 5,
            "favorite": True,
            "review": "Great coffee",
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["rating"] == 5
    assert data["favorite"] is True
    assert data["review"] == "Great coffee"
    assert data["cafe"]["name"] == "Activity Test Café"
    assert "id" in data
    assert "createdAt" in data


def test_list_activities_with_data(client: TestClient, test_user: dict):
    client.post(
        "/cafes",
        json={
            "name": "Café A",
            "address": "1 St",
            "mapsId": "place_a",
            "mapsUrl": "https://maps.google.com/place_a",
        },
    )
    cafe_id = client.post(
        "/cafes",
        json={
            "name": "Café B",
            "address": "2 St",
            "mapsId": "place_b",
            "mapsUrl": "https://maps.google.com/place_b",
        },
    ).json()["id"]
    client.post(
        "/auth/login",
        json={"emailOrUsername": test_user["email"], "password": test_user["password"]},
    )
    user_id = client.get("/me").json()["id"]
    client.post(
        "/activities",
        json={"userId": user_id, "cafeId": cafe_id, "rating": 4, "favorite": False, "review": None},
    )
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["rating"] == 4
    assert "cafe" in data[0]


def test_get_user_activities(client: TestClient, test_user: dict):
    cafe_resp = client.post(
        "/cafes",
        json={
            "name": "User Act Café",
            "address": "3 St",
            "mapsId": "place_user_act",
            "mapsUrl": "https://maps.google.com/place_user_act",
        },
    )
    cafe_id = cafe_resp.json()["id"]
    client.post(
        "/auth/login",
        json={"emailOrUsername": test_user["email"], "password": test_user["password"]},
    )
    user_id = client.get("/me").json()["id"]
    client.post(
        "/activities",
        json={"userId": user_id, "cafeId": cafe_id, "rating": 3, "favorite": True, "review": "Nice"},
    )
    resp = client.get(f"/activities/{test_user['username']}")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["review"] == "Nice"


def test_get_user_activities_unknown_user(client: TestClient):
    resp = client.get("/activities/nonexistentuser123")
    assert resp.status_code == 200
    assert resp.json() == []


def test_feed_requires_auth(client: TestClient):
    resp = client.get("/activities/feed")
    assert resp.status_code == 401


def test_feed_returns_own_activities(client: TestClient, test_user: dict, auth_headers: dict):
    cafe_resp = client.post(
        "/cafes",
        json={
            "name": "Feed Café",
            "address": "4 St",
            "mapsId": "place_feed",
            "mapsUrl": "https://maps.google.com/place_feed",
        },
    )
    cafe_id = cafe_resp.json()["id"]
    client.post(
        "/auth/login",
        json={"emailOrUsername": test_user["email"], "password": test_user["password"]},
    )
    user_id = client.get("/me").json()["id"]
    client.post(
        "/activities",
        json={"userId": user_id, "cafeId": cafe_id, "rating": 5, "favorite": True, "review": "Feed"},
    )
    resp = client.get("/activities/feed")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["review"] == "Feed"
    assert "user" in data[0]
