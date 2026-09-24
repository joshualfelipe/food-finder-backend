from dto.conversation_dto import Message, MessageResponse
from repository import conversation_repository
from typing import List


def start_conversation(message: Message, user_id: str) -> MessageResponse:
    if message.thread_id is None:
        message.thread_id = conversation_repository.create_new_thread(user_id)
    return conversation_repository.save_message(message)


def get_messages(thread_id: str, role: str | None) -> List[MessageResponse]:
    return conversation_repository.get_messages_from_thread(thread_id, role)
