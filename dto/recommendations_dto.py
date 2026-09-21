from pydantic import BaseModel


class PlacesRequest(BaseModel):
    latitude: float
    longitude: float
