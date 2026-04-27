from fastapi import APIRouter

from handler import openai_handler

router = APIRouter(tags=["OpenAI"])


@router.get("/openai")
async def openai():
    return openai_handler.chat_food_recommendations()
