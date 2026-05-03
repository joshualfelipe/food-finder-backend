from config import settings
from dto.geoapify_dto import GeoapifyParamsDTO
from dto.recommendations_dto import PlacesRequest
from handler import ai_recommendations_handler, ai_chat_handler
from haversine import haversine, Unit
from service import geoapify_service


async def recommendations(
    request: PlacesRequest,
    user_message: str | None = None,
):
    features = ai_chat_handler.resolve_search_parameters(user_message)

    params = GeoapifyParamsDTO(
        lat=request.latitude,
        lon=request.longitude,
        features=features,
        apiKey=settings.GEOAPIFY_API_KEY,
    )

    response = await geoapify_service.geoapify_conn(params)

    restaurants_features = response.json().get("features", [])[1:]
    origin = (request.latitude, request.longitude)
    restaurants = []

    for feature in restaurants_features:
        props = feature.get("properties") or {}

        name = props.get("name")
        lat = props.get("lat")
        lon = props.get("lon")
        if not name:
            continue

        catering = props.get("catering") or {}
        facilities = props.get("facilities") or {}
        distance_m = haversine(origin, (lat, lon), unit=Unit.METERS)

        restaurant_data = {
            "name": name,
            "catering_cuisine": catering.get("cuisine"),
            "categories": props.get("categories", []),
            "facilities_takeaway": facilities.get("takeaway"),
            "distance_m": distance_m,
        }

        restaurants.append(restaurant_data)

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
