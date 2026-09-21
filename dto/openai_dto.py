from pydantic import BaseModel
from typing import List


class AIMessage(BaseModel):
    role: str
    content: str


class OpenAIChatRequestDTO(BaseModel):
    messages: List[AIMessage]
    max_completion_tokens: int
    temperature: float
