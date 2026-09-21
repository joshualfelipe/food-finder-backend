from dto.recommendations_dto import PlacesRequest
from fastapi import APIRouter
from handler import restaurant_recommendations_handler

router = APIRouter(tags=["Recommendations"])


@router.get("/recommendations")
async def geoapify_recommendations(
    latitude: float, longitude: float, user_message: str | None = None
):
    location = PlacesRequest(latitude=latitude, longitude=longitude)
    return await restaurant_recommendations_handler.recommendations(
        location, user_message
    )
