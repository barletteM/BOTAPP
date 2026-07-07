from datetime import datetime
from pydantic import BaseModel


class PastedKnowledgeCreate(BaseModel):
    title: str
    text: str
    change_note: str = "Pasted website/manual text"


class KnowledgeDocumentRead(BaseModel):
    id: str
    bot_id: str
    title: str
    source_type: str
    file_name: str
    current_version: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class KnowledgeVersionRead(BaseModel):
    id: str
    document_id: str
    version: int
    content_hash: str
    change_note: str
    created_at: datetime

    class Config:
        from_attributes = True
