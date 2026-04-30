from pydantic import BaseModel
from typing import List


class PlacesRequest(BaseModel):
    latitude: float
    longitude: float


class PlacesFilter(BaseModel):
    radius: int | None
    min_price: int | None
    max_price: int | None
    open_now: bool | None
    category_ids: List[str] | None
    limit: int | None


class AIRecommendations(BaseModel):
    name: str
    reason: str


class Place(BaseModel):
    latitude: float
    longitude: float
    name: str
    address: str
    description: str | None
    distance: float
    price: float | None
    rating: float | None


class RestaurantRecommendationsResponse(BaseModel):
    ai_recommendations: AIRecommendations | None
    restaurants: List[Place] | None
    count: int | None
    message: str
