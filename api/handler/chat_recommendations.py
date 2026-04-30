from openai import OpenAI
from config import settings
import json
from prompt import SYSTEM_PROMPT

client = OpenAI(api_key=settings.OPENAI_API_KEY)


def chat_food_recommendations(
    user_message: str, restaurant_data: list, conversation_history: list | None = None
):
    if conversation_history is None:
        conversation_history = []

    clean_restaurant_data = [
        {
            "name": item.get("name"),
            "distance": item.get("distance"),
            "type": item.get("categories", [{}])[0].get("name", "").lower(),
            "address": item.get("location", {}).get("formatted_address", ""),
        }
        for item in restaurant_data
    ]

    # Keep memory small (token optimization)
    trimmed_history = conversation_history[-6:]

    messages = [
        {"role": "developer", "content": SYSTEM_PROMPT},
        *trimmed_history,
        {
            "role": "user",
            "content": f"""
User Query:
{user_message}

Available Restaurants (SOURCE OF TRUTH):
{json.dumps(clean_restaurant_data, ensure_ascii=False)}
""",
        },
    ]

    response = client.chat.completions.create(
        model="gpt-5.4-nano",
        messages=messages,
        response_format={"type": "json_object"},
        temperature=0.2,
    )

    raw_content = response.choices[0].message.content or "{}"

    try:
        result = (
            json.loads(raw_content) if isinstance(raw_content, str) else raw_content
        )
    except json.JSONDecodeError:
        # If the model somehow returned invalid JSON, keep it machine-readable for the API.
        result = {"error": "invalid_ai_json", "raw": raw_content}

    # Optional: update history (for caller to store)
    # conversation_history.append({"role": "user", "content": user_message})
    # conversation_history.append({"role": "assistant", "content": raw_content})

    return result, conversation_history
