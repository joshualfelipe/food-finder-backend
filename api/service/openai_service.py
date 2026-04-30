from openai import OpenAI
from config import settings
from dto.openai_dto import OpenAIChatRequestDTO

client = OpenAI(api_key=settings.OPENAI_API_KEY)


def openai_conn(params: OpenAIChatRequestDTO):
    return client.chat.completions.create(
        model="gpt-5.4-nano",
        response_format={"type": "json_object"},
        messages=params.messages,
        max_completion_tokens=params.max_completion_tokens,
        temperature=params.temperature,
    )
