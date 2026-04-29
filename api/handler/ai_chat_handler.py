from prompt_chat import PARAMETER_MATCHING_PROMPT, ALL_VALID_FEATURES
from config import settings
from openai import OpenAI
import json

client = OpenAI(api_key=settings.OPENAI_API_KEY)
PARAMETER_MATCHING_CONFIG = {
    "model": "gpt-5.4-nano",
    "temperature": 0.0,
    "max_completion_tokens": 80,
    "top_p": 1.0,
    "response_format": {"type": "json_object"},
}


def resolve_search_parameters(user_message: str) -> list[str]:
    DEFAULT_FEATURES = ["radius_500.restaurant", "radius_500.cafe"]

    response = client.chat.completions.create(
        messages=[
            {"role": "system", "content": PARAMETER_MATCHING_PROMPT},
            {"role": "user", "content": user_message},
        ],
        **PARAMETER_MATCHING_CONFIG,
    )

    raw = response.choices[0].message.content

    print(raw)

    try:
        parsed = json.loads(raw)
        features = parsed.get("features", [])

        valid = [f for f in features if f in ALL_VALID_FEATURES]

        if not valid:
            return DEFAULT_FEATURES

        return valid

    except (json.JSONDecodeError, KeyError, TypeError):
        return DEFAULT_FEATURES
