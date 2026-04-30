from config import settings
from dto.fsq_dto import FourSquarePlacesRequest
import httpx


async def fsq_conn(params: FourSquarePlacesRequest) -> list:
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.FOURSQUARE_BASE_URL}",
            params=params,
            headers={
                "X-Places-Api-Version": settings.FOURSQUARE_X_PLACES_API_VERSION,
                "authorization": f"Bearer {settings.FOURSQUARE_API_KEY}",
            },
        )

        return [item for item in response.json().get("results", [])]
