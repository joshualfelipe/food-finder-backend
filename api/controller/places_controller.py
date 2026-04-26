from fastapi import APIRouter
from dto.places_dto import PlacesRequest
from handler import places_handler

router = APIRouter(tags=["Places"])


@router.get("/places")
async def places(latitude: float, longitude: float):
    request = PlacesRequest(latitude=latitude, longitude=longitude)
    return await places_handler.places(request)
