import json
from prompt import SYSTEM_PROMPT
from service import openai_service
from dto.openai_dto import OpenAIChatRequestDTO


def chat_food_recommendations(
    user_message: str, restaurant_data: list, conversation_history: list | None = None
):
    # TODO: Implement conversation history
    formatted_chat_history = format_conversation_history(conversation_history)

    messages = format_ai_chat_prompt(
        restaurant_data, formatted_chat_history, user_message
    )

    params = OpenAIChatRequestDTO(
        messages=messages, max_completion_tokens=500, temperature=0.7
    )

    response = openai_service.openai_conn(params)

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
    return conversation_history[-6:]


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
