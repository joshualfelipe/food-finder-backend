from controller.auth_controller import get_current_user
from fastapi import APIRouter, Depends
from dto.conversation_dto import Message
from dto.auth_dto import MeResponseDTO
from handler import conversation_handler

router = APIRouter(tags=["Conversation"])


@router.post("/send_message")
async def send_message(
    message: Message, user: MeResponseDTO = Depends(get_current_user)
):
    # User is logged in so set role to user message
    message.role = "user"

    return conversation_handler.start_conversation(message, user.user_id)


@router.get("/get_messages")
async def get_messages(
    thread_id: str,
    role: str | None = None,
    user: MeResponseDTO = Depends(get_current_user),
):
    return conversation_handler.get_messages(thread_id, role)
