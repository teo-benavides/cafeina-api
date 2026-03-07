"""Tests for places service (Google Places API); client is mocked."""

import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.schemas.cafe import CafeBase


def _make_mock_place(name: str, place_id: str, maps_uri: str, route: str = "", number: str = ""):
    """Build a mock place like the Google Places API response."""
    comps = []
    if route:
        c = MagicMock()
        c.types = ["route"]
        c.short_text = route
        comps.append(c)
    if number:
        c = MagicMock()
        c.types = ["street_number"]
        c.short_text = number
        comps.append(c)
    place = MagicMock()
    place.display_name = MagicMock(text=name)
    place.id = place_id
    place.google_maps_uri = maps_uri
    place.address_components = comps
    return place


def test_search_cafes_returns_cafe_base_list():
    """search_cafes maps Google response to CafeBase using display_name, id, google_maps_uri, address_components."""
    from app.services.places import search_cafes

    mock_place1 = _make_mock_place("Café Alpha", "place_1", "https://maps.google.com/place_1", "Main St", "100")
    mock_place2 = _make_mock_place("Café Beta", "place_2", "https://maps.google.com/place_2", "Oak Ave", "200")
    mock_response = MagicMock()
    mock_response.places = [mock_place1, mock_place2]

    with patch("app.services.places.client") as mock_client:
        mock_client.search_nearby = AsyncMock(return_value=mock_response)
        result = asyncio.run(search_cafes((40.7, -74.0), 5000.0))

    assert len(result) == 2
    assert result[0].name == "Café Alpha"
    assert result[0].maps_id == "place_1"
    assert result[0].maps_url == "https://maps.google.com/place_1"
    assert result[0].address == "Main St 100"
    assert result[1].name == "Café Beta"
    assert result[1].address == "Oak Ave 200"
    assert isinstance(result[0], CafeBase)


def test_search_cafes_empty_places():
    """search_cafes returns empty list when no places."""
    from app.services.places import search_cafes

    mock_response = MagicMock()
    mock_response.places = []

    with patch("app.services.places.client") as mock_client:
        mock_client.search_nearby = AsyncMock(return_value=mock_response)
        result = asyncio.run(search_cafes((0.0, 0.0), 1000.0))

    assert result == []
