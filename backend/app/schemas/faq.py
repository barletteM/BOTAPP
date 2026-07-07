from datetime import datetime
from pydantic import BaseModel


class FAQCreate(BaseModel):
    question: str
    answer: str


class FAQUpdate(BaseModel):
    question: str | None = None
    answer: str | None = None


class FAQRead(BaseModel):
    id: str
    bot_id: str
    question: str
    answer: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
