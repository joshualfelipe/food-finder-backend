from pydantic import BaseModel
from typing import List


class PlacesRequest(BaseModel):
    latitude: float
    longitude: float


class FourSquarePlacesRequest(BaseModel):
    ll: str  # latitude,longitude
    radius: int  # in meters
    fsq_category_ids: List[str]
    min_price: int | None
    max_price: int | None
    open_now: bool
    limit: int


class Place(BaseModel):
    latitude: float
    longitude: float
    name: str
    address: str
    description: str | None
    distance: float
    price: float | None
    rating: float | None


class PlacesResponse(BaseModel):
    places: List[Place]
    count: int
