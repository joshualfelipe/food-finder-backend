from fastapi import Query
from dto.conversation_dto import ConversationResponse, Message, MessageResponse
from postgrest.exceptions import APIError
from service import supabase_client
from datetime import datetime, timezone
from typing import List


def create_new_thread(user_id: str) -> str:
    response = (
        supabase_client.db_client.table("threads")
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


def get_thread(thread_id: str) -> ConversationResponse | None:
    try:
        response = (
            supabase_client.db_client.table("threads")
            .select("id, user_id, created_at, updated_at, deleted_at")
            .eq("id", thread_id)
            .is_("deleted_at", None)
            .limit(1)
            .execute()
        )
    except APIError as error:
        # 22P02: malformed id (e.g. not a valid uuid) — treat as not found
        if error.code == "22P02":
            return None
        raise

    if not response.data:
        return None

    row = response.data[0]
    return ConversationResponse.model_validate({**row, "thread_id": row["id"]})


def save_message(message: Message) -> MessageResponse:
    message_response = (
        supabase_client.db_client.table("messages")
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

    supabase_client.db_client.table("threads").update(
        {"updated_at": datetime.now(timezone.utc).isoformat()}
    ).eq("id", message.thread_id).execute()

    return MessageResponse.model_validate(message_response.data[0])


def get_messages_from_thread(thread_id: str, role: str | None) -> List[MessageResponse]:
    query = (
        supabase_client.db_client.table("messages")
        .select("*")
        .eq("thread_id", thread_id)
        .is_("deleted_at", None)
    )

    if role:
        query = query.eq("role", role)

    response = query.order("created_at", desc=True).limit(20).execute()

    messages = [MessageResponse.model_validate(row) for row in response.data]
    return list(reversed(messages))
