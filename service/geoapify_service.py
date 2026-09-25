from config import settings
from dto.geoapify_dto import GeoapifyParamsDTO
import httpx


async def geoapify_conn(params: GeoapifyParamsDTO) -> httpx.Response:
    async with httpx.AsyncClient(timeout=httpx.Timeout(20.0)) as client:
        response = await client.get(
            f"{settings.GEOAPIFY_BASE_URL}",
            params=params.model_dump(exclude_none=True),
        )
        # Geoapify errors have no "features" key, so without this they'd look
        # like "no restaurants nearby" instead of failing
        response.raise_for_status()
        return response
