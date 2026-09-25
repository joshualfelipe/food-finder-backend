import json
from config import settings
from dto.geoapify_dto import GeoapifyParamsDTO
from dto.recommendations_dto import PlacesRequest
from dto.conversation_dto import Message
from handler import ai_recommendations_handler, conversation_handler
from haversine import haversine, Unit
from service import geoapify_service
from dto.auth_dto import MeResponseDTO

WIDEST_FEATURES = ["drive_15.restaurant", "drive_15.cafe"]

AI_VISIBLE_FIELDS = (
    "name",
    "catering_cuisine",
    "categories",
    "facilities_takeaway",
    "distance_m",
)

CLIENT_VISIBLE_FIELDS = (
    "name",
    "latitude",
    "longitude",
    "catering_cuisine",
    "distance_m",
)

MAX_AI_CANDIDATES = 60


def _parse_restaurant(feature: dict, origin: tuple[float, float]) -> dict | None:
    props = feature.get("properties") or {}

    name = props.get("name")
    if not name:
        return None

    latitude = props.get("lat")
    longitude = props.get("lon")
    catering = props.get("catering") or {}
    facilities = props.get("facilities") or {}

    return {
        "name": name,
        "latitude": latitude,
        "longitude": longitude,
        "catering_cuisine": catering.get("cuisine"),
        "categories": props.get("categories", []),
        "facilities_takeaway": facilities.get("takeaway"),
        "distance_m": haversine(origin, (latitude, longitude), unit=Unit.METERS),
    }


async def recommendations(
    request: PlacesRequest,
    message: Message,
    user: MeResponseDTO,
):
    message_history = (
        conversation_handler.get_messages(message.thread_id, user.user_id)
        if message.thread_id
        else None
    )
    new_message = conversation_handler.create_message(
        message, user.user_id, verify_owner=False
    )

    params = GeoapifyParamsDTO(
        lat=request.latitude,
        lon=request.longitude,
        features=WIDEST_FEATURES,
        apiKey=settings.GEOAPIFY_API_KEY,
    )
    response = await geoapify_service.geoapify_conn(params)
    place_features = response.json().get("features", [])[1:]
    origin = (request.latitude, request.longitude)

    restaurants = []
    seen_names = set()
    for feature in place_features:
        restaurant = _parse_restaurant(feature, origin)
        if restaurant is None or restaurant["name"] in seen_names:
            continue
        seen_names.add(restaurant["name"])
        restaurants.append(restaurant)

    ai_candidates = sorted(restaurants, key=lambda r: r["distance_m"])[
        :MAX_AI_CANDIDATES
    ]
    ai_restaurant_data = [
        {field: restaurant[field] for field in AI_VISIBLE_FIELDS}
        for restaurant in ai_candidates
    ]
    ai_response = ai_recommendations_handler.chat_food_recommendations(
        ai_restaurant_data, message_history, new_message
    )
    summary = ai_recommendations_handler.extract_chat_text(ai_response)
    ai_recommendations_payload = ai_response
    if isinstance(ai_response, dict):
        ai_recommendations_payload = {}
        for key, value in ai_response.items():
            if key in ("summary", "message"):
                continue
            ai_recommendations_payload[key] = value

    bot_content = summary
    if isinstance(ai_recommendations_payload, dict) and ai_recommendations_payload.get(
        "recommendations"
    ):
        recommended = json.dumps(
            ai_recommendations_payload["recommendations"], ensure_ascii=False
        )
        bot_content = f"{summary}\nRecommended: {recommended}"

    conversation_handler.create_message(
        Message(
            thread_id=new_message.thread_id,
            role="bot",
            content=bot_content,
        ),
        user.user_id,
        verify_owner=False,
    )

    client_restaurants = [
        {field: restaurant[field] for field in CLIENT_VISIBLE_FIELDS}
        for restaurant in restaurants
    ]

    return {
        "thread_id": new_message.thread_id,
        "summary": summary,
        "ai_recommendations": ai_recommendations_payload,
        "restaurants": client_restaurants,
        "count": len(client_restaurants),
        "message": "Recommendations fetched successfully.",
    }
