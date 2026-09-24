from config import settings
from openai import OpenAI
from prompt import SYSTEM_PROMPT
import json

client = OpenAI(api_key=settings.OPENAI_API_KEY)


def chat_food_recommendations(
    user_message: str, restaurant_data: list, conversation_history: list | None = None
):
    # TODO: Implement conversation history
    formatted_chat_history = format_conversation_history(conversation_history)

    messages = format_ai_chat_prompt(
        restaurant_data, formatted_chat_history, user_message
    )

    response = client.chat.completions.create(
        model="gpt-5.4-nano",
        messages=messages,
        response_format={"type": "json_object"},
        max_completion_tokens=500,
        temperature=0.7,
    )

    raw_content = response.choices[0].message.content or "{}"

    try:
        result = (
            json.loads(raw_content) if isinstance(raw_content, str) else raw_content
        )
    except json.JSONDecodeError:
        # If the model somehow returned invalid JSON, keep it machine-readable for the API.
        result = {"error": "invalid_ai_json", "raw": raw_content}

    # TODO: Implement conversation history
    return result, formatted_chat_history


def format_conversation_history(conversation_history: list | None) -> list:
    if conversation_history is None:
        return []

    # Keep memory small (token optimization)
    return conversation_history[-10:]


def format_ai_chat_prompt(
    restaurant_data: list, formatted_chat_history: list, user_message: str
) -> list:
    return [
        {"role": "developer", "content": SYSTEM_PROMPT},
        *formatted_chat_history,
        {
            "role": "user",
            "content": f"User Query: {user_message}\nAvailable Restaurants (SOURCE OF TRUTH):\n{json.dumps(restaurant_data, ensure_ascii=False)}",
        },
    ]
