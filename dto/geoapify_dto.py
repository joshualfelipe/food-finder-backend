from pydantic import BaseModel


class GeoapifyParamsDTO(BaseModel):
    categories: str
    filter: str
    bias: str
    limit: int
    apiKey: str
