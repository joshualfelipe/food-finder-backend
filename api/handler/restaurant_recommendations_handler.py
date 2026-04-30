from dto.recommendations_dto import (
    PlacesRequest,
    Place,
    RestaurantRecommendationsResponse,
    PlacesFilter,
)
from dto.fsq_dto import FourSquarePlacesRequest
import httpx
from config import settings
from handler import ai_recommendations_handler
from service import fsq_service


async def recommendations(
    request: PlacesRequest,
    message: str | None = None,
    filters: PlacesFilter | None = None,
) -> RestaurantRecommendationsResponse:
    params: FourSquarePlacesRequest = {
        "ll": f"{request.latitude},{request.longitude}",
        "radius": filters.radius if filters.radius else 1000,
        "fsq_category_ids": (
            filters.category_ids
            if filters.category_ids
            else ["63be6904847c3692a84b9bb5"]
        ),
        "min_price": filters.min_price if filters.min_price else 1,
        "max_price": filters.max_price if filters.max_price else 4,
        "open_now": filters.open_now if filters.open_now is not None else False,
        "limit": filters.limit if filters.limit else 25,
    }

    restaurants_in_the_area = await fsq_service.fsq_conn(params)

    if restaurants_in_the_area is None:
        return {"message": "No restaurants found."}

    raw_restaurant_data = strip_raw_restaurant_data(restaurants_in_the_area)

    # TODO: implement conversation history for future memory implementation
    ai_response, _ = ai_recommendations_handler.chat_food_recommendations(
        message,
        raw_restaurant_data,
        None,
    )

    formatted_restaurant_data = list(map(map_place, restaurants_in_the_area))

    return {
        "ai_recommendations": ai_response,
        "restaurants": formatted_restaurant_data,
        "count": len(formatted_restaurant_data),
        "message": "Recommendations fetched successfully.",
    }


def strip_raw_restaurant_data(restaurant_data: list) -> list:
    return [
        {
            "name": item.get("name"),
            "distance": item.get("distance"),
            "type": item.get("categories", [{}])[0].get("name", "").lower(),
            "address": item.get("location", {}).get("formatted_address", ""),
        }
        for item in restaurant_data
    ]


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
