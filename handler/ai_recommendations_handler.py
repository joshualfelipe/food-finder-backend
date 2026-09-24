from dto.openai_dto import OpenAIChatRequestDTO
from dto.conversation_dto import MessageResponse
from typing import List
import json
from prompt import AI_RECOMMENDATION_PROMPT
from service import openai_service


def chat_food_recommendations(
    restaurant_data: list,
    message_history: List[MessageResponse] | None,
    message: MessageResponse,
):
    formatted_chat_history = format_conversation_history(message_history)

    messages = format_ai_chat_prompt(restaurant_data, formatted_chat_history, message)

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

    return result


def format_conversation_history(
    conversation_history: List[MessageResponse] | None,
) -> list:
    if conversation_history is None:
        return []

    message_history = []
    for message in conversation_history:
        message_history.append(
            {
                "role": message.role if message.role == "user" else "assistant",
                "content": message.content,
            }
        )
    return message_history[-6:]


def format_ai_chat_prompt(
    restaurant_data: list, formatted_chat_history: list, message: MessageResponse
) -> list:
    return [
        {"role": "developer", "content": AI_RECOMMENDATION_PROMPT},
        *formatted_chat_history,
        {
            "role": "user",
            "content": f"User Query: {message.content}\nAvailable Restaurants (SOURCE OF TRUTH):\n{json.dumps(restaurant_data, ensure_ascii=False)}",
        },
    ]
