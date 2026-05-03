from dto.recommendations_dto import PlacesRequest, PlacesFilter
from fastapi import APIRouter
from handler import (
    restaurant_recommendations_handler,
    restaurant_recommendations_v1_handler,
)

router = APIRouter(tags=["Recommendations"])


@router.get("/v2/recommendations")
async def geoapify_recommendations(
    latitude: float, longitude: float, user_message: str | None = None
):
    location = PlacesRequest(latitude=latitude, longitude=longitude)
    return await restaurant_recommendations_handler.recommendations(
        location, user_message
    )


@router.get("/v1/recommendations")
async def fsq_recommendations(
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
    return await restaurant_recommendations_v1_handler.recommendations(
        location, user_message, filters
    )
