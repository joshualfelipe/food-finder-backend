from dto.places_dto import (
    PlacesRequest,
    FourSquarePlacesRequest,
    Place,
    PlacesResponse,
)
import httpx
from config import settings
from handler import openai_handler


async def places(request: PlacesRequest):
    params: FourSquarePlacesRequest = {
        "ll": f"{request.latitude},{request.longitude}",
        "radius": 20000,
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

        response = [item for item in response.json().get("results", [])]
        ai, _ = openai_handler.chat_food_recommendations(
            "restaurants near me excellent to celebrate my dad'd 60th birthday. price is not an issue. we want a nice ambiance and good food. we are open to all cuisines. I also want it near a mall or hotel so we can do some shopping or stay the night after. we want to be able to walk to the restaurant from the hotel or mall.",
            response,
            None,
        )

        # Map the response to the desired format
        response2 = list(map(map_place, response))

        return {
            # "count": len(response),
            "ai": ai,
            "places": response2,
        }


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
