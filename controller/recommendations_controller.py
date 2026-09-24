from controller.auth_controller import get_current_user
from dto.auth_dto import MeResponseDTO
from dto.recommendations_dto import PlacesRequest
from dto.conversation_dto import Message
from fastapi import APIRouter, Depends
from handler import restaurant_recommendations_handler

router = APIRouter(tags=["Recommendations"])


@router.get("/recommendations")
async def geoapify_recommendations(
    latitude: float,
    longitude: float,
    user_message: str,
    thread_id: str | None = None,
    user: MeResponseDTO = Depends(get_current_user),
):
    location = PlacesRequest(latitude=latitude, longitude=longitude)
    message = Message(thread_id=thread_id, role="user", content=user_message)
    return await restaurant_recommendations_handler.recommendations(
        location, message, user
    )
