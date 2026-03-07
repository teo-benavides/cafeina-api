"""Tests for cafe CRUD operations and slug generation."""

import pytest
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.crud.cafe import (
    get_cafes,
    get_cafe_by_slug,
    get_cafe_by_maps_id,
    create_cafe,
)
from app.schemas.cafe import CafeCreate


def test_get_cafes_empty(db: Session):
    assert get_cafes(db) == []


def test_create_cafe(db: Session):
    cafe_in = CafeCreate(
        name="My Café",
        address="1 Main St",
        maps_id="place_1",
        maps_url="https://maps.google.com/place_1",
    )
    cafe = create_cafe(db, cafe_in)
    assert cafe.id is not None
    assert cafe.name == "My Café"
    assert cafe.slug
    assert "cafe" in cafe.slug.lower() or "my" in cafe.slug.lower()


def test_create_cafe_duplicate_maps_id_raises(db: Session):
    cafe_in = CafeCreate(
        name="First",
        address="1 St",
        maps_id="same_id",
        maps_url="https://maps.google.com/same",
    )
    create_cafe(db, cafe_in)
    with pytest.raises(HTTPException) as exc_info:
        create_cafe(db, CafeCreate(
            name="Second",
            address="2 St",
            maps_id="same_id",
            maps_url="https://maps.google.com/same",
        ))
    assert exc_info.value.status_code == 400


def test_get_cafe_by_slug(db: Session):
    cafe_in = CafeCreate(
        name="Slug Café",
        address="2 Oak Ave",
        maps_id="place_2",
        maps_url="https://maps.google.com/place_2",
    )
    created = create_cafe(db, cafe_in)
    found = get_cafe_by_slug(db, created.slug)
    assert found is not None
    assert found.id == created.id


def test_get_cafe_by_maps_id(db: Session):
    cafe_in = CafeCreate(
        name="Maps Café",
        address="3 Pine Rd",
        maps_id="place_maps_3",
        maps_url="https://maps.google.com/place_maps_3",
    )
    created = create_cafe(db, cafe_in)
    found = get_cafe_by_maps_id(db, "place_maps_3")
    assert found is not None
    assert found.id == created.id


def test_slugify_diacritics(db: Session):
    """Café with accent should produce a slug without it."""
    cafe_in = CafeCreate(
        name="Café Résumé",
        address="4 Elm St",
        maps_id="place_4",
        maps_url="https://maps.google.com/place_4",
    )
    cafe = create_cafe(db, cafe_in)
    assert "é" not in cafe.slug
    assert "è" not in cafe.slug


def test_slug_name_plus_address_when_name_collides(db: Session):
    """When base_slug exists, use name + address for slug."""
    create_cafe(db, CafeCreate(name="Cafe", address="1 First St", maps_id="p_a", maps_url="https://x.com/a"))
    cafe2 = create_cafe(db, CafeCreate(name="Cafe", address="2 Second St", maps_id="p_b", maps_url="https://x.com/b"))
    assert cafe2.slug
    assert "cafe" in cafe2.slug.lower()
    assert "2" in cafe2.slug or "second" in cafe2.slug.lower()


def test_slug_uid_fallback_when_name_address_collides(db: Session):
    """When name+address slug also exists, use uid suffix."""
    create_cafe(db, CafeCreate(name="Cafe", address="Same St", maps_id="p_x", maps_url="https://x.com/x"))
    create_cafe(db, CafeCreate(name="Cafe", address="Same St", maps_id="p_y", maps_url="https://x.com/y"))
    cafe3 = create_cafe(db, CafeCreate(name="Cafe", address="Same St", maps_id="p_z", maps_url="https://x.com/z"))
    assert cafe3.slug
    assert len(cafe3.slug) >= 10  # base + hyphen + 6-char uid


def test_slug_empty_name_fallback(db: Session):
    """Name that slugifies to empty gets base_slug 'cafe'."""
    cafe = create_cafe(db, CafeCreate(name="---", address="X", maps_id="p_empty", maps_url="https://x.com/e"))
    assert cafe.slug
    assert "cafe" in cafe.slug.lower()


def test_slug_name_address_empty_uses_addr_suffix(db: Session):
    """When name+address slugifies to empty, use base_slug-addr."""
    create_cafe(db, CafeCreate(name="---", address="---", maps_id="p1", maps_url="https://x.com/1"))
    cafe2 = create_cafe(db, CafeCreate(name="---", address="---", maps_id="p2", maps_url="https://x.com/2"))
    assert "addr" in cafe2.slug
    assert "cafe" in cafe2.slug.lower()
