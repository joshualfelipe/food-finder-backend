from pydantic import BaseModel
from typing import List


class GeoapifyParamsDTO(BaseModel):
    lat: float
    lon: float
    features: List[str]
    apiKey: str
