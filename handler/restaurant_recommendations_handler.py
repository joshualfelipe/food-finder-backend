from config import settings
from dto.geoapify_dto import GeoapifyParamsDTO
from dto.recommendations_dto import PlacesRequest
from dto.conversation_dto import Message
from handler import ai_recommendations_handler, ai_chat_handler, conversation_handler
from haversine import haversine, Unit
from service import geoapify_service
from dto.auth_dto import MeResponseDTO
import json


async def recommendations(
    request: PlacesRequest,
    message: Message,
    user: MeResponseDTO,
):
    if message.thread_id:
        message_history = conversation_handler.get_messages(message.thread_id)
    else:
        message_history = None

    new_message = conversation_handler.create_message(message, user.user_id)

    features = ai_chat_handler.resolve_search_parameters(message.content)

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

    ai_response = ai_recommendations_handler.chat_food_recommendations(
        restaurants, message_history, new_message
    )

    conversation_handler.create_message(
        Message(
            thread_id=new_message.thread_id,
            role="bot",
            content=json.dumps(ai_response),
        ),
        user.user_id,
    )

    return {
        "ai_recommendations": ai_response,
        "restaurants": restaurants,
        "count": len(restaurants),
        "message": "Recommendations fetched successfully.",
        "thread_id": new_message.thread_id,
    }
