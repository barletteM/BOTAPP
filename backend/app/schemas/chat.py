from datetime import datetime
from pydantic import BaseModel


class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None
    visitor_name: str = ""


class ChatResponse(BaseModel):
    session_id: str
    answer: str


class ChatMessageRead(BaseModel):
    id: str
    role: str
    content: str
    created_at: datetime

    class Config:
        from_attributes = True


class ChatSessionRead(BaseModel):
    id: str
    bot_id: str
    visitor_name: str
    created_at: datetime
    messages: list[ChatMessageRead] = []

    class Config:
        from_attributes = True
