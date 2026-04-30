from dto.recommendations_dto import (
    PlacesRequest,
)
from dto.geoapify_dto import GeoapifyParamsDTO
from config import settings
from haversine import haversine, Unit
from handler import ai_recommendations_handler
from service import geoapify_service


async def fetch_geoapify_places(
    request: PlacesRequest,
    user_message: str | None = None,
    features: list[str] | None = None,
):
    params = GeoapifyParamsDTO(
        lat=request.latitude,
        lon=request.longitude,
        features=features,
        apiKey=settings.GEOAPIFY_API_KEY,
    )

    response = await geoapify_service.geoapify_conn(params)

    features = response.json().get("features", [])
    restaurants_data = features[1:]

    restaurants = []
    for restaurant in restaurants_data:

        name = restaurant.get("properties", {}).get("name")
        catering_cuisine = (
            restaurant.get("properties", {}).get("catering", {}).get("cuisine", None)
        )
        categories = restaurant.get("properties", {}).get("categories", [])
        facilities_takeaway = (
            restaurant.get("properties", {}).get("facilities", {}).get("takeaway", None)
        )
        distance_m = haversine(
            (request.latitude, request.longitude),
            (restaurant["properties"]["lat"], restaurant["properties"]["lon"]),
            unit=Unit.METERS,
        )
        if name:
            restaurants.append(
                {
                    "name": name,
                    "catering_cuisine": catering_cuisine,
                    "categories": categories,
                    "facilities_takeaway": facilities_takeaway,
                    "distance_m": distance_m,
                }
            )

    # return {
    #     "restaurants": restaurants,
    #     "count": len(restaurants),
    #     "message": "Recommendations fetched successfully.",
    # }

    ai_response, _ = ai_recommendations_handler.chat_food_recommendations(
        user_message,
        restaurants,
        None,
    )

    return {
        "ai_recommendations": ai_response,
        "restaurants": restaurants,
        "count": len(restaurants),
        "message": "Recommendations fetched successfully.",
    }
