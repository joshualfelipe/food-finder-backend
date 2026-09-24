from fastapi import Query
from dto.conversation_dto import Message, MessageResponse
from service import supabase_client
from datetime import datetime, timezone
from typing import List


def create_new_thread(user_id: str) -> str:
    response = (
        supabase_client.client.table("threads")
        .insert(
            {
                "user_id": user_id,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat(),
                "deleted_at": None,
            }
        )
        .execute()
    )

    return response.data[0]["id"]


def save_message(message: Message) -> MessageResponse:
    message_response = (
        supabase_client.client.table("messages")
        .insert(
            {
                "thread_id": message.thread_id,
                "role": message.role,
                "content": message.content,
                "created_at": datetime.now(timezone.utc).isoformat(),
            }
        )
        .execute()
    )

    supabase_client.client.table("threads").update(
        {"updated_at": datetime.now(timezone.utc).isoformat()}
    ).eq("id", message.thread_id).execute()

    return MessageResponse.model_validate(message_response.data[0])


def get_messages_from_thread(thread_id: str, role: str | None) -> List[MessageResponse]:
    query = (
        supabase_client.client.table("messages")
        .select("*")
        .eq("thread_id", thread_id)
        .is_("deleted_at", None)
    )

    if role:
        query.eq("role", role)

    response = query.order("created_at", desc=False).limit(20).execute()

    messages = [MessageResponse.model_validate(row) for row in response.data]
    return list(reversed(messages))
