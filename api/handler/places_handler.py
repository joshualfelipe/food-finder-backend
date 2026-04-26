from dto.places_dto import (
    PlacesRequest,
    FourSquarePlacesRequest,
    Place,
    PlacesResponse,
)
import httpx
from config import settings


async def places(request: PlacesRequest):
    params: FourSquarePlacesRequest = {
        "ll": f"{request.latitude},{request.longitude}",
        "radius": 5000,
        "fsq_category_ids": ["63be6904847c3692a84b9bb5"],
        "min_price": 1,
        "max_price": 4,
        "open_now": True,
        "limit": 50,
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.FOURSQUARE_BASE_URL}",
            params=params,
            headers={
                "X-Places-Api-Version": settings.FOURSQUARE_X_PLACES_API_VERSION,
                "authorization": f"Bearer {settings.FOURSQUARE_API_KEY}",
            },
        )

        # Map the response to the desired format
        response = [map_place(item) for item in response.json().get("results", [])]
        return PlacesResponse(places=response, count=len(response))


def map_place(item: dict) -> Place:
    return Place(
        latitude=item.get("latitude"),
        longitude=item.get("longitude"),
        name=item.get("name"),
        address=item.get("location", {}).get("formatted_address"),
        description=item.get("description", ""),
        distance=item.get("distance"),
        price=item.get("price"),
        rating=item.get("rating"),
    )
