from dto.conversation_dto import Message, MessageResponse
from fastapi import HTTPException, status
from repository import conversation_repository
from typing import List


def assert_thread_owner(thread_id: str, user_id: str) -> None:
    thread = conversation_repository.get_thread(thread_id)
    if thread is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Thread not found."
        )
    if thread.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this thread.",
        )


def create_message(
    message: Message, user_id: str, verify_owner: bool = True
) -> MessageResponse:
    if message.thread_id is None:
        message.thread_id = conversation_repository.create_new_thread(user_id)
    elif verify_owner:
        assert_thread_owner(message.thread_id, user_id)
    return conversation_repository.save_message(message)


def get_messages(
    thread_id: str, user_id: str, role: str | None = None
) -> List[MessageResponse]:
    assert_thread_owner(thread_id, user_id)
    return conversation_repository.get_messages_from_thread(thread_id, role)
