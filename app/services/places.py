from google.maps import places_v1
from google.type import latlng_pb2
from app.schemas.cafe import CafeBase
from app.config import settings

client = places_v1.PlacesAsyncClient(client_options={"api_key": settings.GOOGLE_MAPS_API_KEY})

async def search_cafes(location: tuple[float, float], radius: float) -> list[CafeBase]:
    # Define the coordinates and radius
    lat, lng = location
    radius_meters = radius
    # Create the LatLng object for the center
    center_point = latlng_pb2.LatLng(latitude=lat, longitude=lng)
    # Create the circle
    circle_area = places_v1.types.Circle(
        center=center_point,
        radius=radius_meters
    )
    # Add the circle to the location restriction
    location_restriction = places_v1.SearchNearbyRequest.LocationRestriction(
        circle=circle_area
    )
    # Build the request
    request = places_v1.SearchNearbyRequest(
        location_restriction=location_restriction,
        included_types=["cafe"]
    )
    # Set the field mask
    fieldMask = "places.displayName,places.addressComponents,places.id,places.googleMapsUri"
    # Make the request
    response = await client.search_nearby(request=request, metadata=[("x-goog-fieldmask",fieldMask)])

    cafes: list[CafeBase] = []
    for place in response.places:
        cafe = CafeBase(
            name=place.display_name.text,
            address="",
            mapsId=place.id,
            mapsUrl=place.google_maps_uri
        )
        route = ""
        number = ""
        for c in place.address_components:
            if "route" in c.types:
                route = c.short_text
            if "street_number" in c.types:
                number = c.short_text
        cafe.address = f"{route} {number}"
        cafes.append(cafe)
    return cafes