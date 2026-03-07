"""Tests for /cafes endpoints."""

import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient

from app.schemas.cafe import CafeBase


def test_list_cafes_empty(client: TestClient):
    resp = client.get("/cafes")
    assert resp.status_code == 200
    assert resp.json() == []


def test_list_cafes_with_data(client: TestClient):
    client.post(
        "/cafes",
        json={
            "name": "First Café",
            "address": "100 Main St",
            "mapsId": "place_first",
            "mapsUrl": "https://maps.google.com/place_first",
        },
    )
    client.post(
        "/cafes",
        json={
            "name": "Second Café",
            "address": "200 Oak Ave",
            "mapsId": "place_second",
            "mapsUrl": "https://maps.google.com/place_second",
        },
    )
    resp = client.get("/cafes")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 2
    names = {c["name"] for c in data}
    assert names == {"First Café", "Second Café"}
    for cafe in data:
        assert "id" in cafe
        assert "slug" in cafe
        assert "address" in cafe
        assert "mapsId" in cafe
        assert "mapsUrl" in cafe


def test_add_cafe(client: TestClient):
    resp = client.post(
        "/cafes",
        json={
            "name": "Test Café",
            "address": "123 Main St",
            "mapsId": "place_abc123",
            "mapsUrl": "https://maps.google.com/place_abc123",
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "Test Café"
    assert data["address"] == "123 Main St"
    assert data["mapsId"] == "place_abc123"
    assert data["mapsUrl"] == "https://maps.google.com/place_abc123"
    assert "slug" in data
    assert "id" in data


def test_add_cafe_duplicate_maps_id(client: TestClient):
    payload = {
        "name": "First Café",
        "address": "123 Main St",
        "mapsId": "place_same",
        "mapsUrl": "https://maps.google.com/place_same",
    }
    client.post("/cafes", json=payload)
    resp = client.post(
        "/cafes",
        json={
            "name": "Second Café",
            "address": "456 Other St",
            "mapsId": "place_same",
            "mapsUrl": "https://maps.google.com/place_same",
        },
    )
    assert resp.status_code == 400
    assert "already exists" in resp.json()["detail"].lower()


def test_get_cafe_by_slug(client: TestClient):
    create = client.post(
        "/cafes",
        json={
            "name": "Slug Test Café",
            "address": "789 Oak Ave",
            "mapsId": "place_slug123",
            "mapsUrl": "https://maps.google.com/place_slug123",
        },
    )
    assert create.status_code == 200
    slug = create.json()["slug"]
    resp = client.get(f"/cafes/{slug}")
    assert resp.status_code == 200
    assert resp.json()["slug"] == slug
    assert resp.json()["name"] == "Slug Test Café"


def test_get_cafe_by_slug_not_found(client: TestClient):
    resp = client.get("/cafes/nonexistent-slug-xyz")
    assert resp.status_code == 404
    assert "not found" in resp.json()["detail"].lower()


def test_get_nearby_cafes_search_mocked(client: TestClient):
    """GET /cafes/search returns places from Google; we mock search_cafes."""
    mock_cafes = [
        CafeBase(
            name="Mock Café One",
            address="100 Main St",
            maps_id="place_mock_1",
            maps_url="https://maps.google.com/place_mock_1",
        ),
        CafeBase(
            name="Mock Café Two",
            address="200 Oak Ave",
            maps_id="place_mock_2",
            maps_url="https://maps.google.com/place_mock_2",
        ),
    ]
    with patch("app.api.cafe.search_cafes", new_callable=AsyncMock, return_value=mock_cafes):
        resp = client.get("/cafes/search?lat=40.7&lng=-74.0&radius=5000")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 2
    names = {c["name"] for c in data}
    assert names == {"Mock Café One", "Mock Café Two"}
    for cafe in data:
        assert "mapsId" in cafe
        assert "mapsUrl" in cafe
        assert "address" in cafe
