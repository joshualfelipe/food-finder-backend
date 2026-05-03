from pydantic import BaseModel
from typing import List


class FourSquarePlacesRequest(BaseModel):
    ll: str  # latitude,longitude
    radius: int  # in meters
    fsq_category_ids: List[str]
    min_price: int | None
    max_price: int | None
    open_now: bool
    limit: int
