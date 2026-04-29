from fastapi import APIRouter
from dto.recommendations_dto import PlacesRequest, PlacesFilter
from handler import (
    restaurant_recommendations_handler,
    geoapify_handler,
    ai_chat_handler,
)

router = APIRouter(tags=["Places"])


@router.get("/recommendations")
async def recommendations(
    latitude: float,
    longitude: float,
    user_message: str | None = None,
    radius: int | None = None,
    min_price: int | None = None,
    max_price: int | None = None,
    open_now: bool | None = None,
    category_ids: str | None = None,
    limit: int | None = None,
):
    location = PlacesRequest(latitude=latitude, longitude=longitude)
    filters = PlacesFilter(
        radius=radius,
        min_price=min_price,
        max_price=max_price,
        open_now=open_now,
        category_ids=category_ids.split(",") if category_ids else None,
        limit=limit,
    )
    return await restaurant_recommendations_handler.recommendations(
        location, user_message, filters
    )


@router.get("/geoapify")
async def geoapify(latitude: float, longitude: float, user_message: str | None = None):
    features = ai_chat_handler.resolve_search_parameters(user_message)
    location = PlacesRequest(latitude=latitude, longitude=longitude)
    return await geoapify_handler.fetch_geoapify_places(
        location, user_message, features
    )


@router.get("/test/chat")
async def test_chat_recommendations(user_message: str):
    return ai_chat_handler.resolve_search_parameters(user_message)
