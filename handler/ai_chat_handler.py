from dto.openai_dto import OpenAIChatRequestDTO
from prompt import PARAMETER_MATCHING_PROMPT, ALL_VALID_FEATURES
from service import openai_service
import json


def resolve_search_parameters(user_message: str | None) -> list[str]:
    DEFAULT_FEATURES = ["radius_500.restaurant", "radius_500.cafe"]

    if not user_message:
        return DEFAULT_FEATURES

    params = OpenAIChatRequestDTO(
        messages=[
            {"role": "system", "content": PARAMETER_MATCHING_PROMPT},
            {"role": "user", "content": user_message},
        ],
        max_completion_tokens=80,
        temperature=0.0,
    )

    response = openai_service.openai_conn(params)
    raw = response.choices[0].message.content

    try:
        parsed = json.loads(raw)
        features = parsed.get("features", [])

        valid = [f for f in features if f in ALL_VALID_FEATURES]

        if not valid:
            return DEFAULT_FEATURES

        return valid

    except (json.JSONDecodeError, KeyError, TypeError):
        return DEFAULT_FEATURES
