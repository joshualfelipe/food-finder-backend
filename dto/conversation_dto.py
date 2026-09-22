from pydantic import BaseModel
from datetime import datetime


class Conversation(BaseModel):
    thread_id: str | None
    user_id: str


class ConversationResponse(Conversation):
    created_at: datetime
    updated_at: datetime | None
    deleted_at: datetime | None


class Message(BaseModel):
    thread_id: str | None
    role: str | None
    content: str


class MessageResponse(Message):
    created_at: datetime
    deleted_at: datetime | None
