from controller.auth_controller import get_current_user
from fastapi import APIRouter, Depends
from dto.conversation_dto import Message
from dto.auth_dto import MeResponseDTO

router = APIRouter(tags=["Conversation"])


@router.post("/start")
async def start_conversation(
    message: Message, user: MeResponseDTO = Depends(get_current_user)
):
    return message
