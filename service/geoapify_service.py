from config import settings
from dto.geoapify_dto import GeoapifyParamsDTO
import httpx


async def geoapify_conn(params: GeoapifyParamsDTO) -> httpx.Response:
    async with httpx.AsyncClient() as client:
        return await client.get(
            f"{settings.GEOAPIFY_BASE_URL}",
            params=params.model_dump(exclude_none=True),
        )
